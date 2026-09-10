"""
Real MinIO / S3-compatible object storage service.

Uses the synchronous `minio` SDK (v7.x) wrapped with asyncio.run_in_executor
so it integrates cleanly with FastAPI's async request handlers.
"""

import asyncio
import io
from functools import partial
from typing import Optional
from datetime import timedelta

from minio import Minio
from minio.error import S3Error

from app.core.config import settings


def _build_client(endpoint: str) -> Minio:
    """Create a MinIO client for a given endpoint."""
    secure = endpoint.startswith("https://")
    host = endpoint.replace("https://", "").replace("http://", "")
    return Minio(
        host,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=secure,
        region="us-east-1",
    )


# Shared client instances
_minio_client: Optional[Minio] = None
_minio_public_client: Optional[Minio] = None


def get_minio_client() -> Minio:
    global _minio_client
    if _minio_client is None:
        _minio_client = _build_client(settings.MINIO_ENDPOINT)
    return _minio_client


def get_minio_public_client() -> Minio:
    global _minio_public_client
    if _minio_public_client is None:
        public_ep = getattr(settings, "MINIO_PUBLIC_ENDPOINT", None) or settings.MINIO_ENDPOINT
        _minio_public_client = _build_client(public_ep)
    return _minio_public_client


class StorageService:
    """
    Async wrapper around the synchronous MinIO SDK.
    All heavy operations are offloaded to a thread pool executor.
    """

    def __init__(self, bucket_name: str = None) -> None:
        self.bucket_name = bucket_name or settings.MINIO_BUCKET_NAME
        self._client = get_minio_client()

    # ──────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────

    def _ensure_bucket(self) -> None:
        """Create the bucket if it doesn't already exist."""
        client = self._client
        if not client.bucket_exists(self.bucket_name):
            client.make_bucket(self.bucket_name)

    def _upload_sync(self, key: str, data: bytes, content_type: str) -> None:
        self._ensure_bucket()
        self._client.put_object(
            self.bucket_name,
            key,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    def _delete_sync(self, key: str) -> None:
        try:
            self._client.remove_object(self.bucket_name, key)
        except S3Error:
            pass  # Object may already be gone

    def _get_sync(self, key: str) -> Optional[bytes]:
        try:
            self._ensure_bucket()
            response = self._client.get_object(self.bucket_name, key)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except Exception as e:
            print(f"[StorageService] get_object error for {key}: {e}")
            return None

    def _presigned_url_sync(self, key: str, expires_seconds: int, response_headers: dict = None) -> str:
        self._ensure_bucket()
        expires = timedelta(seconds=expires_seconds)
        kwargs = dict(
            bucket_name=self.bucket_name,
            object_name=key,
            expires=expires,
        )
        if response_headers:
            kwargs["response_headers"] = response_headers
        public_client = get_minio_public_client()
        return public_client.presigned_get_object(**kwargs)

    # ──────────────────────────────────────────────
    # Public async API
    # ──────────────────────────────────────────────

    async def upload_file(self, key: str, data: bytes, content_type: str) -> None:
        """Upload binary data to MinIO under the given object key."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, partial(self._upload_sync, key, data, content_type))

    async def get_file(self, key: str) -> Optional[bytes]:
        """Download binary data from MinIO for the given object key."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(self._get_sync, key))

    async def delete_file(self, key: str) -> None:
        """Delete an object from MinIO. Silently succeeds if already gone."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, partial(self._delete_sync, key))

    async def get_presigned_url(
        self,
        key: str,
        expires_seconds: int = 3600,
        inline: bool = False,
        response_content_type: Optional[str] = None,
    ) -> str:
        """
        Return a temporary presigned GET URL for the given object key.

        - `inline=True`  → browser opens the file (e.g., PDF viewer, HTML5 video).
        - `inline=False` → browser downloads the file.
        """
        headers = {}
        if inline:
            headers["response-content-disposition"] = "inline"
        else:
            headers["response-content-disposition"] = "attachment"

        if response_content_type:
            headers["response-content-type"] = response_content_type

        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(
            None,
            partial(self._presigned_url_sync, key, expires_seconds, headers if headers else None),
        )
        return url
