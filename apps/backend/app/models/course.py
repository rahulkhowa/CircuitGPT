from typing import Optional, List
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Course(BaseModel):
    __tablename__ = "courses"

    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    semester: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    modules: Mapped[List["Module"]] = relationship(back_populates="course", lazy="selectin", cascade="all, delete-orphan")
    quizzes: Mapped[List["Quiz"]] = relationship(back_populates="course", lazy="selectin")
    uploads: Mapped[List["Upload"]] = relationship(back_populates="course", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Course id={self.id} code={self.code} title={self.title}>"
