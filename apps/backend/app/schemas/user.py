from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.role import UserRole


# ──────────────────────────────────────────────
# Request schemas
# ──────────────────────────────────────────────

class UserCreate(BaseModel):
    """Payload for POST /auth/register"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.STUDENT


class UserUpdate(BaseModel):
    """Payload for PATCH /users/me"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=512)


class PasswordChange(BaseModel):
    """Payload for POST /users/me/change-password"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


# ──────────────────────────────────────────────
# Response schemas
# ──────────────────────────────────────────────

class UserResponse(BaseModel):
    """Public user representation returned to clients"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ──────────────────────────────────────────────
# Auth / Token schemas
# ──────────────────────────────────────────────

class TokenResponse(BaseModel):
    """JWT pair returned on successful login or token refresh"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None



class LoginRequest(BaseModel):
    """Payload for POST /auth/login"""
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Payload for POST /auth/refresh"""
    refresh_token: str


class MessageResponse(BaseModel):
    """Generic message envelope"""
    message: str
