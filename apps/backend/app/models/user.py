from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.role import UserRole

if TYPE_CHECKING:
    from app.models.chat_history import ChatHistory
    from app.models.memory import Memory
    from app.models.upload import Upload



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
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Active core relationships
    uploads: Mapped[list["Upload"]] = relationship(back_populates="uploaded_by", lazy="selectin")
    chat_histories: Mapped[list["ChatHistory"]] = relationship(back_populates="user", lazy="selectin")
    memories: Mapped[list["Memory"]] = relationship(back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
