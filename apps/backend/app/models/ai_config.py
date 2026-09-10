import uuid
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class AIConfiguration(BaseModel):
    __tablename__ = "ai_configurations"

    system_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model: Mapped[str] = mapped_column(String(100), default="nvidia/nemotron-3-ultra-550b-a55b", nullable=False)
    context_window: Mapped[int] = mapped_column(Integer, default=32000, nullable=False)
    retrieval_top_k: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    memory_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reasoning_effort: Mapped[str] = mapped_column(String(20), default="high", nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    def __repr__(self) -> str:
        return f"<AIConfiguration system_id={self.system_id} model={self.model}>"
