import uuid
import enum
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class NoteStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class Note(BaseModel):
    __tablename__ = "notes"

    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("modules.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[NoteStatus] = mapped_column(
        SAEnum(NoteStatus, name="notestatus"), default=NoteStatus.DRAFT, nullable=False
    )
    tags: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)  # CSV of tags

    # Relationships
    author: Mapped["User"] = relationship(back_populates="notes")
    module: Mapped[Optional["Module"]] = relationship(back_populates="notes")
    evaluations: Mapped[List["NoteEvaluation"]] = relationship(back_populates="note", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Note id={self.id} title={self.title} status={self.status}>"
