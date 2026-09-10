from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory
from app.repositories.base import BaseRepository


class MemoryRepository(BaseRepository[Memory]):
    """
    Repository for user long-term memory items, strictly scoped by user_id and system_id.
    """

    model = Memory

    async def get_by_user_and_system(
        self, user_id: UUID, system_id: Optional[str] = None, memory_type: Optional[str] = None, limit: int = 50
    ) -> List[Memory]:
        """Fetch memories strictly for a user within a specific system scope."""
        stmt = select(Memory).where(Memory.user_id == user_id)
        if system_id:
            stmt = stmt.where(or_(Memory.system_id == system_id, Memory.system_id.is_(None)))
        if memory_type:
            stmt = stmt.where(Memory.key == memory_type)
        result = await self.db.execute(stmt.limit(limit))
        return list(result.scalars().all())

    async def get_by_user(
        self, user_id: UUID, memory_type: Optional[str] = None, limit: int = 50
    ) -> List[Memory]:
        """Fetch memories for a user."""
        return await self.get_by_user_and_system(user_id=user_id, memory_type=memory_type, limit=limit)
