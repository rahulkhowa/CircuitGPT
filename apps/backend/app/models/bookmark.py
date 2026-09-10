import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Bookmark(BaseModel):
    __tablename__ = "bookmarks"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)    # "note" | "quiz" | "upload" | "module"
    resource_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="bookmarks")

    def __repr__(self) -> str:
        return f"<Bookmark id={self.id} user_id={self.user_id} resource_type={self.resource_type}>"
