from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.upload import Upload, ResourceType
from app.repositories.base import BaseRepository


class UploadRepository(BaseRepository[Upload]):
    model = Upload

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    @classmethod
    def from_session(cls, db: AsyncSession) -> "UploadRepository":
        return cls(db)

    async def list_for_system(
        self,
        subject_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        skip: int = 0,
        limit: int = 200,
    ) -> List[Upload]:
        """Return all shared uploads, optionally filtered by subject and/or resource type."""
        stmt = select(Upload)
        if subject_id and subject_id != "all":
            stmt = stmt.where(Upload.subject_id == subject_id)
        if resource_type:
            stmt = stmt.where(Upload.resource_type == resource_type)
        stmt = stmt.order_by(Upload.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_for_user(
        self,
        user_id: UUID,
        subject_id: str,
        resource_type: ResourceType,
        skip: int = 0,
        limit: int = 200,
    ) -> List[Upload]:
        """Return all uploads belonging to `user_id` for a specific subject + resource type."""
        stmt = (
            select(Upload)
            .where(Upload.uploaded_by_id == user_id)
            .where(Upload.subject_id == subject_id)
            .where(Upload.resource_type == resource_type)
            .order_by(Upload.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, upload_id: UUID) -> Optional[Upload]:
        """Fetch a single upload by its ID, regardless of who owns it."""
        stmt = select(Upload).where(Upload.id == upload_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_owned_by_user(self, upload_id: UUID, user_id: UUID) -> Optional[Upload]:
        """Fetch a single upload only if it belongs to the given user (ownership check)."""
        stmt = (
            select(Upload)
            .where(Upload.id == upload_id)
            .where(Upload.uploaded_by_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
