import uuid
from typing import Optional, List
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Quiz(BaseModel):
    __tablename__ = "quizzes"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("modules.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    questions: Mapped[Optional[dict]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)   # [{question, options, answer_key, points}]
    total_marks: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    course: Mapped["Course"] = relationship(back_populates="quizzes")
    module: Mapped[Optional["Module"]] = relationship(back_populates="quizzes")
    attempts: Mapped[List["QuizAttempt"]] = relationship(back_populates="quiz", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Quiz id={self.id} title={self.title} course_id={self.course_id}>"
