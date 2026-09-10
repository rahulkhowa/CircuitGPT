from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_admin
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, PasswordChange, MessageResponse
from app.services.user import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Fetch current authenticated user profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile details for current user."""
    service = UserService(db)
    updated_user = await service.update_profile(current_user, payload)
    return UserResponse.model_validate(updated_user)


@router.post("/me/change-password", response_model=MessageResponse)
async def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change password for current user."""
    service = UserService(db)
    await service.change_password(current_user, payload.current_password, payload.new_password)
    return MessageResponse(message="Password successfully updated.")


@router.get("", response_model=List[UserResponse], dependencies=[Depends(require_admin)])
async def list_all_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Admin-only: List all registered users."""
    from app.repositories.user import UserRepository
    repo = UserRepository.from_session(db)
    users = await repo.get_multi(skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]
