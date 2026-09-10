from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.memory import MemoryRepository
from app.schemas.memory import MemoryCreate, MemoryResponse, MemoryRecallQuery


class MemoryService:
    """
    Long-term memory service for recording student preferences, mastery, and misconceptions.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = MemoryRepository(db)

    async def add_memory(self, user_id: UUID, payload: MemoryCreate) -> MemoryResponse:
        memory_obj = await self.repo.create(
            {
                "user_id": user_id,
                "memory_type": payload.memory_type,
                "content": payload.content,
                "context": payload.context,
                "tags": payload.tags,
                "importance": payload.importance,
            }
        )
        return MemoryResponse.model_validate(memory_obj)

    async def recall_memories(self, user_id: UUID, query: MemoryRecallQuery) -> List[MemoryResponse]:
        memories = await self.repo.get_by_user(user_id=user_id, limit=query.top_k)
        return [MemoryResponse.model_validate(m) for m in memories]
