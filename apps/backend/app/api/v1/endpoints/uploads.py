"""
Real resource upload/management endpoint.

Routes:
  POST   /api/v1/uploads               – upload a file for a subject + resource type
  GET    /api/v1/uploads               – list current user's uploads (filtered by subject + type)
  GET    /api/v1/uploads/{id}/view     – get presigned URL to open in browser
  GET    /api/v1/uploads/{id}/download – get presigned URL to download
  DELETE /api/v1/uploads/{id}          – delete own resource from MinIO + DB
"""

import mimetypes
import os
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.cache import cache_service
from app.core.config import settings
from app.models.upload import ResourceType, Upload
from app.models.user import User
from app.repositories.upload import UploadRepository
from app.services.storage import StorageService

router = APIRouter()

# ──────────────────────────────────────────────
# Allowed extensions per resource type
# ──────────────────────────────────────────────

_ALLOWED: dict[ResourceType, set[str]] = {
    ResourceType.NOTES:       {".pdf", ".doc", ".docx"},
    ResourceType.VIDEOS:      {".mp4", ".webm", ".mkv", ".mov"},
    ResourceType.LAB_MANUALS: {".pdf", ".doc", ".docx"},
    ResourceType.BOOKS:       {".pdf"},
    ResourceType.PYQS:        {".pdf"},
}

_MIME_FALLBACK: dict[str, str] = {
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mkv": "video/x-matroska",
    ".mov": "video/quicktime",
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _validate_file(resource_type: ResourceType, filename: str, size_bytes: int) -> None:
    ext = os.path.splitext(filename)[-1].lower()
    allowed = _ALLOWED.get(resource_type, set())
    if ext not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File type '{ext}' is not allowed for {resource_type.value}. "
                   f"Allowed: {', '.join(sorted(allowed))}",
        )
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )


# ──────────────────────────────────────────────
# Pydantic schemas
# ──────────────────────────────────────────────

from app.models.upload import ResourceType, UploadStatus
from app.services.rag.pipeline import RAGPipeline

rag_pipeline = RAGPipeline()

# ──────────────────────────────────────────────
# Pydantic schemas
# ──────────────────────────────────────────────

class UploadOut(BaseModel):
    id: UUID
    subject_id: str
    resource_type: ResourceType
    original_name: str
    mime_type: str
    file_size_bytes: int | None
    status: UploadStatus
    created_at: str

    model_config = {"from_attributes": True}


class PresignedUrlOut(BaseModel):
    url: str


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@router.post("", response_model=UploadOut, status_code=status.HTTP_201_CREATED)
async def upload_resource(
    file: UploadFile = File(...),
    subject_id: str = Form(...),
    resource_type: ResourceType = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a resource file for a subject.
    - Validates file type and size.
    - Stores the actual file in MinIO.
    - Persists metadata in PostgreSQL with status UPLOADED -> PROCESSING -> INDEXED.
    - Ingests content into shared system RAG vector store.
    """
    contents = await file.read()
    original_name = file.filename or "file"
    ext = os.path.splitext(original_name)[-1].lower()

    mime_type = file.content_type
    if not mime_type or mime_type == "application/octet-stream":
        guessed, _ = mimetypes.guess_type(original_name)
        mime_type = guessed or _MIME_FALLBACK.get(ext, "application/octet-stream")

    size_bytes = len(contents)

    _validate_file(resource_type, original_name, size_bytes)

    unique_filename = f"{uuid4()}{ext}"
    minio_key = f"subjects/{subject_id}/{resource_type.value}/{current_user.id}/{unique_filename}"

    storage = StorageService()

    # 1. Upload to MinIO first — if this fails, don't touch DB
    try:
        await storage.upload_file(minio_key, contents, mime_type)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to store file: {exc}",
        ) from exc

    # 2. Persist metadata to PostgreSQL in PROCESSING state
    try:
        repo = UploadRepository.from_session(db)
        upload: Upload = await repo.create(
            {
                "uploaded_by_id": current_user.id,
                "subject_id": subject_id,
                "resource_type": resource_type,
                "original_name": original_name,
                "filename": unique_filename,
                "mime_type": mime_type,
                "file_size_bytes": size_bytes,
                "minio_key": minio_key,
                "status": UploadStatus.PROCESSING,
            }
        )
    except Exception as exc:
        try:
            await storage.delete_file(minio_key)
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save resource metadata: {exc}",
        ) from exc

    # 3. Automatic System RAG Ingestion
    try:
        if resource_type == ResourceType.VIDEOS:
            await rag_pipeline.ingest_video(
                video_filename=original_name,
                system_id=subject_id,
                resource_id=str(upload.id),
            )
        else:
            text_content = ""
            ext_lower = ext.lower()
            if ext_lower == ".pdf":
                try:
                    import io

                    import pypdf
                    reader = pypdf.PdfReader(io.BytesIO(contents))
                    pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                    text_content = "\n\n".join(pages).strip()
                except Exception as e:
                    print(f"[Uploads] PDF extraction warning: {e}")

            if not text_content:
                try:
                    text_content = contents.decode("utf-8", errors="ignore").strip()
                except Exception:
                    pass

            if not text_content:
                text_content = f"Resource document: {original_name} for subject {subject_id}"

            await rag_pipeline.ingest_document(
                content=text_content,
                file_name=original_name,
                system_id=subject_id,
                resource_type=resource_type.value,
                resource_id=str(upload.id),
            )

        upload.status = UploadStatus.INDEXED
        await db.commit()
        await db.refresh(upload)

        # Invalidate search cache on new resource upload
        await cache_service.delete_pattern("cache:search:*")
    except Exception as exc:
        print(f"[Uploads] RAG ingestion failed for {upload.id}: {exc}")
        upload.status = UploadStatus.FAILED
        await db.commit()
        await db.refresh(upload)

    return UploadOut(
        id=upload.id,
        subject_id=upload.subject_id,
        resource_type=upload.resource_type,
        original_name=upload.original_name,
        mime_type=upload.mime_type,
        file_size_bytes=upload.file_size_bytes,
        status=upload.status,
        created_at=upload.created_at.isoformat(),
    )


@router.get("", response_model=list[UploadOut])
async def list_resources(
    subject_id: str | None = None,
    resource_type: ResourceType | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all shared system resources, optionally filtered by subject + resource type.
    """
    repo = UploadRepository.from_session(db)
    uploads = await repo.list_for_system(
        subject_id=subject_id,
        resource_type=resource_type,
    )
    return [
        UploadOut(
            id=u.id,
            subject_id=u.subject_id,
            resource_type=u.resource_type,
            original_name=u.original_name,
            mime_type=u.mime_type,
            file_size_bytes=u.file_size_bytes,
            status=u.status if hasattr(u, "status") else UploadStatus.INDEXED,
            created_at=u.created_at.isoformat(),
        )
        for u in uploads
    ]


@router.get("/{upload_id}/view", response_model=PresignedUrlOut)
async def view_resource(
    upload_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return a short-lived presigned URL to view a resource inline in the browser.
    """
    repo = UploadRepository.from_session(db)
    upload = await repo.get_by_id(upload_id)
    if not upload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")

    storage = StorageService()
    url = await storage.get_presigned_url(
        upload.minio_key,
        expires_seconds=3600,
        inline=True,
        response_content_type=upload.mime_type,
    )
    return PresignedUrlOut(url=url)


@router.get("/{upload_id}/download", response_model=PresignedUrlOut)
async def download_resource(
    upload_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return a short-lived presigned URL to download a resource.
    """
    repo = UploadRepository.from_session(db)
    upload = await repo.get_by_id(upload_id)
    if not upload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")

    storage = StorageService()
    url = await storage.get_presigned_url(upload.minio_key, expires_seconds=3600, inline=False)
    return PresignedUrlOut(url=url)


@router.delete("/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    upload_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a resource. Only the uploader can delete their own resource.
    Removes from MinIO and PostgreSQL, and invalidates search caches.
    """
    repo = UploadRepository.from_session(db)
    upload = await repo.get_owned_by_user(upload_id, current_user.id)
    if not upload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")

    minio_key = upload.minio_key

    # Delete from DB first (inside the managed transaction)
    await repo.delete(upload)

    # Delete indexed vectors from vector store
    try:
        await rag_pipeline.delete_resource(str(upload_id))
    except Exception as exc:
        print(f"[Uploads] Vector store cleanup error: {exc}")

    # Invalidate search cache on resource deletion
    await cache_service.delete_pattern("cache:search:*")

    # Then delete from MinIO (best-effort)
    storage = StorageService()
    try:
        await storage.delete_file(minio_key)
    except Exception:
        pass  # Object may already be gone; DB is authoritative


