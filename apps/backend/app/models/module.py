import uuid
from typing import Optional, List
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Module(BaseModel):
    __tablename__ = "modules"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    course: Mapped["Course"] = relationship(back_populates="modules")
    notes: Mapped[List["Note"]] = relationship(back_populates="module", lazy="selectin")
    quizzes: Mapped[List["Quiz"]] = relationship(back_populates="module", lazy="selectin")
    learning_progress: Mapped[List["LearningProgress"]] = relationship(back_populates="module", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Module id={self.id} title={self.title} course_id={self.course_id}>"
