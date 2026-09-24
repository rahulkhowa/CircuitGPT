
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.memory import MemoryCreate, MemoryRecallQuery, MemoryResponse
from app.services.memory import MemoryService

router = APIRouter()


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory_item(
    payload: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Record a new long-term memory entry for the current user.
    """
    service = MemoryService(db)
    return await service.add_memory(current_user.id, payload)


@router.post("/recall", response_model=list[MemoryResponse])
async def recall_memories(
    payload: MemoryRecallQuery,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Recall relevant user memories based on semantic context or tags.
    """
    service = MemoryService(db)
    return await service.recall_memories(current_user.id, payload)
