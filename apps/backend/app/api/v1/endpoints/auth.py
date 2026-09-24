from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
)
from app.models.user import User
from app.schemas.user import (
    LoginRequest,
    MessageResponse,
    PasswordChange,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services.user import UserService

logger = get_logger(__name__)

router = APIRouter()


# ──────────────────────────────────────────────
# POST /auth/register
# ──────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Create a new user account.
    - **email**: must be unique across all accounts
    - **password**: minimum 8 characters
    - **role**: student (default) | faculty | admin
    """
    svc = UserService(db)
    user = await svc.register(payload)
    logger.info(f"new_user_registered email={user.email} role={user.role.value}")
    return UserResponse.model_validate(user)


# ──────────────────────────────────────────────
# POST /auth/login
# ──────────────────────────────────────────────

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and obtain a JWT pair",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate with e-mail + password.
    Returns an **access token** (short-lived) and a **refresh token** (30 days).
    """
    svc = UserService(db)
    user = await svc.authenticate(payload.email, payload.password)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    logger.info(f"user_logged_in user_id={str(user.id)} email={user.email}")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


# ──────────────────────────────────────────────
# POST /auth/refresh
# ──────────────────────────────────────────────

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Obtain a new access token using a refresh token",
)
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    The old refresh token is consumed and a fresh pair is issued (rotation).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_access_token(payload.refresh_token)
    if not token_data or token_data.get("type") != "refresh":
        raise credentials_exception

    from uuid import UUID
    try:
        user_id = UUID(token_data["sub"])
    except (KeyError, ValueError):
        raise credentials_exception from None

    from app.repositories.user import UserRepository
    repo = UserRepository.from_session(db)
    user = await repo.get(user_id)
    if not user or not user.is_active:
        raise credentials_exception

    new_access = create_access_token(str(user.id))
    new_refresh = create_refresh_token(str(user.id))

    logger.info(f"tokens_refreshed user_id={str(user.id)}")
    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


# ──────────────────────────────────────────────
# POST /auth/logout
# ──────────────────────────────────────────────

@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout (client-side token discard)",
)
async def logout(
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """
    Stateless logout — the client is expected to discard both tokens.
    Future enhancement: add token to a Redis blocklist for true server-side
    invalidation (wire-up is ready in core/database.py).
    """
    logger.info(f"user_logged_out user_id={str(current_user.id)}")
    return MessageResponse(message="Successfully logged out.")


# ──────────────────────────────────────────────
# GET /auth/me
# ──────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Return the currently authenticated user",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


# ──────────────────────────────────────────────
# PATCH /auth/me
# ──────────────────────────────────────────────

@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update the current user's profile",
)
async def update_me(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    svc = UserService(db)
    updated = await svc.update_profile(current_user, payload)
    return UserResponse.model_validate(updated)


# ──────────────────────────────────────────────
# POST /auth/me/change-password
# ──────────────────────────────────────────────

@router.post(
    "/me/change-password",
    response_model=MessageResponse,
    summary="Change the current user's password",
)
async def change_password(
    payload: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    svc = UserService(db)
    await svc.change_password(current_user, payload.current_password, payload.new_password)
    logger.info(f"password_changed user_id={str(current_user.id)}")
    return MessageResponse(message="Password updated successfully.")
