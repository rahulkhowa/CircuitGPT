import io
import json
import os
from typing import Any
from uuid import uuid4

import pypdf
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_optional_current_user
from app.core.config import settings
from app.models.chat_history import ChatHistory
from app.models.memory import Memory
from app.models.upload import Upload
from app.models.user import User
from app.services.llm.base import BaseLLMProvider
from app.services.llm.factory import get_llm_provider
from app.services.rag.pipeline import RAGPipeline
from app.services.storage import StorageService

router = APIRouter()
rag_pipeline = RAGPipeline()


class ChatRequest(BaseModel):
    message: str
    subject_code: str | None = "EE101"
    system_id: str | None = "power-system"
    session_id: str | None = None
    resource_type: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    citations: list[dict[str, Any]]
    llm_provider: str


class ConversationOut(BaseModel):
    session_id: str
    title: str
    last_message: str
    message_count: int


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    context_source: str | None = None
    created_at: str


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_ai(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """
    Agentic System-Scoped AI Chat endpoint using NVIDIA Nemotron Ultra + RAG + Multi-Turn Memory.
    Manages context window to prevent token overflow while preserving continuous dialogue.
    """
    _user_id = str(current_user.id) if current_user else "anonymous"  # noqa: F841
    system_id = payload.system_id or payload.subject_code or "general"
    session_id = payload.session_id or str(uuid4())

    # 1. System-Scoped RAG Query
    filters = {"system_id": system_id}
    valid_types = {"notes", "videos", "lab_manuals", "books", "pyqs"}
    if payload.resource_type and payload.resource_type in valid_types:
        filters["resource_type"] = payload.resource_type

    retrieved = await rag_pipeline.query(payload.message, top_k=settings.AI_RAG_TOP_K, filters=filters)

    # Auto-heal: If vector retrieval returned empty, load any existing uploads for this system from DB/MinIO and index on the fly
    if not retrieved:
        try:
            stmt = select(Upload).where(Upload.subject_id == system_id)
            res = await db.execute(stmt)
            system_uploads = res.scalars().all()
            if system_uploads:
                storage = StorageService()
                for up in system_uploads:
                    try:
                        file_bytes = await storage.get_file(up.minio_key)
                        if file_bytes:
                            ext_lower = os.path.splitext(up.original_name)[-1].lower()
                            text_content = ""
                            if ext_lower == ".pdf":
                                try:
                                    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                                    pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                                    text_content = "\n\n".join(pages).strip()
                                except Exception:
                                    pass
                            if not text_content:
                                try:
                                    text_content = file_bytes.decode("utf-8", errors="ignore").strip()
                                except Exception:
                                    pass
                            if text_content:
                                await rag_pipeline.ingest_document(
                                    content=text_content,
                                    file_name=up.original_name,
                                    system_id=up.subject_id,
                                    resource_type=up.resource_type.value if hasattr(up.resource_type, "value") else str(up.resource_type),
                                    resource_id=str(up.id),
                                )
                    except Exception as exc:
                        print(f"[Chat] Fallback auto-ingest error for {up.original_name}: {exc}")

                # Re-query RAG after auto-ingestion
                retrieved = await rag_pipeline.query(payload.message, top_k=settings.AI_RAG_TOP_K, filters=filters)
        except Exception as e:
            print(f"[Chat] Auto-healing RAG error: {e}")

    docs = []
    citations = []
    for item in retrieved:
        payload_data = item.get("payload", {})
        text = payload_data.get("text", "")
        file_name = payload_data.get("file_name", "Course Resource")
        if text:
            docs.append({"title": file_name, "content": text})
            citations.append({"source": file_name, "snippet": text[:120]})

    # 2. User + System Memory Retrieval
    memories = []
    history = []
    if current_user:
        stmt = (
            select(Memory)
            .where(Memory.user_id == current_user.id)
            .where((Memory.system_id == system_id) | (Memory.system_id == None))  # noqa: E711
            .limit(settings.AI_MEMORY_TOP_K)
        )
        mem_res = await db.execute(stmt)
        memories = [{"key": m.key, "value": m.value} for m in mem_res.scalars().all()]

        # Multi-turn conversational continuity: fetch past messages for this session
        hist_stmt = (
            select(ChatHistory)
            .where(ChatHistory.user_id == current_user.id)
            .where(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.created_at.asc())
        )
        hist_res = await db.execute(hist_stmt)
        past_msgs = hist_res.scalars().all()
        max_msgs = getattr(settings, "AI_MAX_RECENT_MESSAGES", 20)
        recent_past = past_msgs[-max_msgs:] if len(past_msgs) > max_msgs else past_msgs
        history = [{"role": m.role, "content": m.content} for m in recent_past]

    context = {
        "docs": docs,
        "memories": memories,
        "citations": citations,
        "history": history,
        "system_id": system_id,
    }

    # 3. LLM Invocation via Provider Abstraction
    llm: BaseLLMProvider = get_llm_provider()
    answer = llm.generate_response(payload.message, context)
    provider_name = "NVIDIA Nemotron Ultra (3-ultra-550b)" if settings.NVIDIA_API_KEY else "MockLLM Engine"

    # 4. Save Chat History to PostgreSQL
    if current_user:
        user_msg = ChatHistory(
            user_id=current_user.id,
            system_id=system_id,
            session_id=session_id,
            role="user",
            content=payload.message,
        )
        ai_msg = ChatHistory(
            user_id=current_user.id,
            system_id=system_id,
            session_id=session_id,
            role="assistant",
            content=answer,
            context_source=citations[0]["source"] if citations else None,
        )
        db.add_all([user_msg, ai_msg])
        await db.commit()

    return ChatResponse(
        session_id=session_id,
        response=answer,
        citations=citations,
        llm_provider=provider_name,
    )


@router.post("/stream")
async def chat_stream_with_ai(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """
    Server-Sent Events (SSE) real-time streaming endpoint for Nemotron Ultra with multi-turn continuity.
    Does not display internal reasoning traces (<think> tags).
    """
    system_id = payload.system_id or payload.subject_code or "general"
    session_id = payload.session_id or str(uuid4())

    filters = {"system_id": system_id}
    if payload.resource_type:
        filters["resource_type"] = payload.resource_type

    retrieved = await rag_pipeline.query(payload.message, top_k=settings.AI_RAG_TOP_K, filters=filters)

    docs = []
    citations = []
    for item in retrieved:
        payload_data = item.get("payload", {})
        text = payload_data.get("text", "")
        file_name = payload_data.get("file_name", "Course Resource")
        if text:
            docs.append({"title": file_name, "content": text})
            citations.append({"source": file_name, "snippet": text[:120]})

    memories = []
    history = []
    if current_user:
        stmt = (
            select(Memory)
            .where(Memory.user_id == current_user.id)
            .where((Memory.system_id == system_id) | (Memory.system_id == None))  # noqa: E711
            .limit(settings.AI_MEMORY_TOP_K)
        )
        mem_res = await db.execute(stmt)
        memories = [{"key": m.key, "value": m.value} for m in mem_res.scalars().all()]

        hist_stmt = (
            select(ChatHistory)
            .where(ChatHistory.user_id == current_user.id)
            .where(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.created_at.asc())
        )
        hist_res = await db.execute(hist_stmt)
        past_msgs = hist_res.scalars().all()
        max_msgs = getattr(settings, "AI_MAX_RECENT_MESSAGES", 20)
        recent_past = past_msgs[-max_msgs:] if len(past_msgs) > max_msgs else past_msgs
        history = [{"role": m.role, "content": m.content} for m in recent_past]

    context = {
        "docs": docs,
        "memories": memories,
        "citations": citations,
        "history": history,
        "system_id": system_id,
    }

    llm: BaseLLMProvider = get_llm_provider()

    async def event_generator():
        # First send metadata and session_id
        yield f"data: {json.dumps({'type': 'metadata', 'session_id': session_id, 'citations': citations})}\n\n"
        accumulated = ""
        async for chunk in llm.stream_response(payload.message, context):
            accumulated += chunk
            yield f"data: {json.dumps({'type': 'token', 'token': chunk})}\n\n"

        # Save to history upon stream completion if user is logged in
        if current_user and accumulated:
            try:
                user_msg = ChatHistory(
                    user_id=current_user.id,
                    system_id=system_id,
                    session_id=session_id,
                    role="user",
                    content=payload.message,
                )
                ai_msg = ChatHistory(
                    user_id=current_user.id,
                    system_id=system_id,
                    session_id=session_id,
                    role="assistant",
                    content=accumulated,
                    context_source=citations[0]["source"] if citations else None,
                )
                db.add_all([user_msg, ai_msg])
                await db.commit()
            except Exception as e:
                print(f"[Chat Stream] Save history warning: {e}")

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/conversations", response_model=list[ConversationOut])
async def list_user_conversations(
    system_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List user's active conversations scoped strictly by (user_id, system_id).
    """
    stmt = (
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .where(ChatHistory.system_id == system_id)
        .order_by(ChatHistory.created_at.desc())
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    # Group by session_id preserving chronological order
    sessions: dict[str, list[ChatHistory]] = {}
    for r in records:
        sessions.setdefault(r.session_id, []).append(r)

    out = []
    for sid, msgs in sessions.items():
        first_user_msg = next((m.content for m in reversed(msgs) if m.role == "user"), "New Conversation")
        out.append(
            ConversationOut(
                session_id=sid,
                title=first_user_msg[:40] + ("..." if len(first_user_msg) > 40 else ""),
                last_message=msgs[0].content[:60],
                message_count=len(msgs),
            )
        )
    return out


@router.get("/conversations/{session_id}", response_model=list[ChatMessageOut])
async def get_conversation_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve full multi-turn chat message history for a specific conversation session.
    """
    stmt = (
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .where(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at.asc())
    )
    result = await db.execute(stmt)
    records = result.scalars().all()
    return [
        ChatMessageOut(
            id=str(r.id),
            role=r.role,
            content=r.content,
            context_source=r.context_source,
            created_at=r.created_at.isoformat() if hasattr(r.created_at, "isoformat") else str(r.created_at),
        )
        for r in records
    ]

