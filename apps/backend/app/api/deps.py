from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal, redis_client
from app.core.security import decode_access_token
from app.models.role import UserRole
from app.models.user import User
from app.repositories.user import UserRepository

# ──────────────────────────────────────────────
# Database / Redis
# ──────────────────────────────────────────────

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency: yields an async SQLAlchemy session.
    Commits on success, rolls back on any unhandled exception.
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis():
    """Dependency: yields the shared async Redis client."""
    yield redis_client


# ──────────────────────────────────────────────
# Current-user resolution
# ──────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Decode the Bearer JWT and return the matching User row.
    Raises 401 if the token is missing, malformed, expired, or the user
    no longer exists / is inactive.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    # token must be an access token (not a refresh token)
    if payload.get("type") != "access":
        raise credentials_exception

    user_id_str: str = payload.get("sub")
    if not user_id_str:
        raise credentials_exception

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception from None

    repo = UserRepository.from_session(db)
    user = await repo.get(user_id)
    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Convenience alias — same as get_current_user but named for clarity."""
    return current_user


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Optional dependency: returns User if valid Bearer token provided, or None if unauthenticated.
    """
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


# ──────────────────────────────────────────────
# RBAC helper
# ──────────────────────────────────────────────

class RoleChecker:
    """
    FastAPI dependency factory for role-based access control.

    Usage::

        @router.get("/admin-only")
        async def admin_only(
            _: User = Depends(RoleChecker([UserRole.ADMIN]))
        ):
            ...
    """

    def __init__(self, allowed_roles: list[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(
        self, current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Operation requires one of: "
                    f"{[r.value for r in self.allowed_roles]}."
                ),
            )
        return current_user


# ──────────────────────────────────────────────
# Convenience role guards
# ──────────────────────────────────────────────

require_admin = RoleChecker([UserRole.ADMIN])
require_faculty_or_admin = RoleChecker([UserRole.FACULTY, UserRole.ADMIN])
require_any_role = RoleChecker([UserRole.STUDENT, UserRole.FACULTY, UserRole.ADMIN])
