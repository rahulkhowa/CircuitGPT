import uuid
from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Notebook(BaseModel):
    __tablename__ = "notebooks"

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Raw markdown blocks
    last_saved_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="notebooks")

    def __repr__(self) -> str:
        return f"<Notebook id={self.id} title={self.title} owner_id={self.owner_id}>"
