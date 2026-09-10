from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """
    Business-logic layer for user management.
    All DB access goes through UserRepository so the service stays testable.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository.from_session(db)

    # ──────────────────────────────────────────────
    # Registration
    # ──────────────────────────────────────────────

    async def register(self, payload: UserCreate) -> User:
        """
        Create a new user account.
        Raises 409 if the e-mail is already taken.
        """
        email = payload.email.lower().strip()

        if await self.repo.email_exists(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this e-mail already exists.",
            )

        user = await self.repo.create(
            {
                "email": email,
                "full_name": payload.full_name,
                "hashed_password": get_password_hash(payload.password),
                "role": payload.role,
                "is_active": True,
                "is_verified": False,
            }
        )
        return user

    # ──────────────────────────────────────────────
    # Authentication
    # ──────────────────────────────────────────────

    async def authenticate(self, email: str, password: str) -> User:
        """
        Verify e-mail + password.
        Raises 401 on any failure (deliberately opaque message).
        """
        user = await self.repo.get_by_email(email.lower().strip())
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid e-mail or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated.",
            )
        return user

    # ──────────────────────────────────────────────
    # Reads
    # ──────────────────────────────────────────────

    async def get_by_id(self, user_id: UUID) -> User:
        user = await self.repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.repo.get_by_email(email)

    # ──────────────────────────────────────────────
    # Updates
    # ──────────────────────────────────────────────

    async def update_profile(self, user: User, payload: UserUpdate) -> User:
        return await self.repo.update(user, payload.model_dump(exclude_unset=True))

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> User:
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )
        return await self.repo.update(
            user, {"hashed_password": get_password_hash(new_password)}
        )

    async def deactivate(self, user: User) -> User:
        return await self.repo.update(user, {"is_active": False})
