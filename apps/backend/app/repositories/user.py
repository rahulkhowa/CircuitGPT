
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    User-specific database operations on top of the generic BaseRepository.
    """

    model = User

    # ──────────────────────────────────────────────
    # Lookup helpers
    # ──────────────────────────────────────────────

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by e-mail address (case-insensitive)."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Return True if an account with this e-mail already exists."""
        return await self.get_by_email(email) is not None

    # ──────────────────────────────────────────────
    # Factory helper — keeps the service layer clean
    # ──────────────────────────────────────────────

    @classmethod
    def from_session(cls, db: AsyncSession) -> "UserRepository":
        repo = cls.__new__(cls)
        repo.db = db
        return repo
