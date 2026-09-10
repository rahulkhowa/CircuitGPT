import uuid
from typing import Optional
from sqlalchemy import Float, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class LearningProgress(BaseModel):
    __tablename__ = "learning_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    completion_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="learning_progress")
    module: Mapped["Module"] = relationship(back_populates="learning_progress")

    def __repr__(self) -> str:
        return f"<LearningProgress user={self.user_id} module={self.module_id} {self.completion_percent:.1f}%>"
