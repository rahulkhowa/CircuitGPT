from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseService(Generic[T]):
    """
    Base service class for domain services.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
