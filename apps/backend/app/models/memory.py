import uuid
from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Memory(BaseModel):
    __tablename__ = "memories"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    system_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)  # System/Subject scope
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)   # e.g. "preferred_topics", "weak_areas"
    value: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="ai", nullable=False)  # "ai" | "user_explicit"
    qdrant_vector_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Cross-ref to vector store

    # Relationships
    user: Mapped["User"] = relationship(back_populates="memories")

    def __repr__(self) -> str:
        return f"<Memory id={self.id} user_id={self.user_id} key={self.key}>"
