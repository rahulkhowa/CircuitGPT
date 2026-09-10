import uuid
from typing import Optional
from sqlalchemy import String, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class NoteEvaluation(BaseModel):
    __tablename__ = "note_evaluations"

    note_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    evaluator_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)          # 0.0 – 10.0
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)       # AI-generated comments
    evaluator_type: Mapped[str] = mapped_column(String(20), default="ai", nullable=False)  # "ai" | "faculty" | "peer"

    # Relationships
    note: Mapped["Note"] = relationship(back_populates="evaluations")

    def __repr__(self) -> str:
        return f"<NoteEvaluation id={self.id} note_id={self.note_id} score={self.score}>"
