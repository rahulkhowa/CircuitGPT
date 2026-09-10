import uuid
from typing import Optional
from sqlalchemy import Float, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class QuizAttempt(BaseModel):
    __tablename__ = "quiz_attempts"

    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    answers: Mapped[Optional[dict]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)       # {question_id: selected_answer}
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_marks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    time_taken_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    quiz: Mapped["Quiz"] = relationship(back_populates="attempts")
    student: Mapped["User"] = relationship(back_populates="quiz_attempts")

    def __repr__(self) -> str:
        return f"<QuizAttempt id={self.id} quiz_id={self.quiz_id} student_id={self.student_id} score={self.score}>"
