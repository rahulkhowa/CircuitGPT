from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notebook import Notebook
from app.repositories.base import BaseRepository


class CircuitRepository(BaseRepository[Notebook]):
    """
    Repository for Circuit schematics, simulation sessions, and notebooks.
    """

    model = Notebook

    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Notebook]:
        """Fetch all notebooks/circuits owned by a user."""
        stmt = (
            select(Notebook)
            .where(Notebook.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_subject(self, user_id: UUID, subject_id: str) -> List[Notebook]:
        """Fetch notebooks/circuits for a specific subject."""
        stmt = select(Notebook).where(
            Notebook.user_id == user_id,
            Notebook.subject_id == subject_id,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
