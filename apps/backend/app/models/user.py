import uuid
from typing import Optional, List
from sqlalchemy import String, Boolean, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
from app.models.role import UserRole


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="userrole"), default=UserRole.STUDENT, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    notes: Mapped[List["Note"]] = relationship(back_populates="author", lazy="selectin")
    notebooks: Mapped[List["Notebook"]] = relationship(back_populates="owner", lazy="selectin")
    quiz_attempts: Mapped[List["QuizAttempt"]] = relationship(back_populates="student", lazy="selectin")
    bookmarks: Mapped[List["Bookmark"]] = relationship(back_populates="user", lazy="selectin")
    learning_progress: Mapped[List["LearningProgress"]] = relationship(back_populates="user", lazy="selectin")
    uploads: Mapped[List["Upload"]] = relationship(back_populates="uploaded_by", lazy="selectin")
    chat_histories: Mapped[List["ChatHistory"]] = relationship(back_populates="user", lazy="selectin")
    memories: Mapped[List["Memory"]] = relationship(back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
