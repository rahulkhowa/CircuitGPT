from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.models.note_evaluation import NoteEvaluation
from app.repositories.base import BaseRepository


class NoteRepository(BaseRepository[Note]):
    """
    Repository for lecture notes and study materials.
    """

    model = Note

    async def get_by_course(self, course_id: UUID, skip: int = 0, limit: int = 50) -> List[Note]:
        """Fetch notes belonging to a course."""
        stmt = select(Note).where(Note.course_id == course_id).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_creator(self, creator_id: UUID) -> List[Note]:
        """Fetch notes created by a specific user."""
        stmt = select(Note).where(Note.created_by_id == creator_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class NoteEvaluationRepository(BaseRepository[NoteEvaluation]):
    """
    Repository for faculty/AI note evaluations.
    """

    model = NoteEvaluation

    async def get_by_note(self, note_id: UUID) -> Optional[NoteEvaluation]:
        """Fetch evaluation for a specific note."""
        stmt = select(NoteEvaluation).where(NoteEvaluation.note_id == note_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_reviews(self) -> List[NoteEvaluation]:
        """Fetch all pending evaluations for faculty review."""
        stmt = select(NoteEvaluation).where(NoteEvaluation.status == "PENDING")
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
