from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic async CRUD repository.

    Subclass and set `model` to the SQLAlchemy ORM class:

        class UserRepository(BaseRepository[User]):
            model = User
    """

    model: Type[ModelType]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ──────────────────────────────────────────────
    # Read
    # ──────────────────────────────────────────────

    async def get(self, id: UUID) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ModelType]:
        """Fetch a paginated list, optionally filtered by exact-match column values."""
        stmt = select(self.model)
        if filters:
            for column, value in filters.items():
                stmt = stmt.where(getattr(self.model, column) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Return row count, optionally filtered."""
        stmt = select(func.count()).select_from(self.model)
        if filters:
            for column, value in filters.items():
                stmt = stmt.where(getattr(self.model, column) == value)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    # ──────────────────────────────────────────────
    # Write
    # ──────────────────────────────────────────────

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Insert a new record and return the persisted instance."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()      # get the generated PK without committing
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: Union[Dict[str, Any], Any],
    ) -> ModelType:
        """Apply a partial update dict (or Pydantic model) to an existing record."""
        if not isinstance(obj_in, dict):
            obj_in = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: ModelType) -> ModelType:
        """Delete a record and return the deleted instance."""
        await self.db.delete(db_obj)
        await self.db.flush()
        return db_obj

    async def exists(self, id: UUID) -> bool:
        """Return True if a record with the given PK exists."""
        stmt = select(func.count()).select_from(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one() > 0
