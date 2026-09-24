import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User



class ChatHistory(BaseModel):
    __tablename__ = "chat_histories"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    system_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)  # System/Subject scope
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)              # "user" | "assistant" | "system"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    context_source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # RAG document source

    # Relationships
    user: Mapped["User"] = relationship(back_populates="chat_histories")

    def __repr__(self) -> str:
        return f"<ChatHistory id={self.id} user_id={self.user_id} role={self.role}>"
