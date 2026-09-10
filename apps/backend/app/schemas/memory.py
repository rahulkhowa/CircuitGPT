from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class MemoryCreate(BaseModel):
    memory_type: str = Field(..., json_schema_extra={"example": "concept_mastery"})
    content: str = Field(..., json_schema_extra={"example": "User understands KCL and Thevenin, struggles with Bode plot phase margin."})
    context: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list, json_schema_extra={"example": ["ee301", "bode_plot"]})
    importance: int = Field(default=3, ge=1, le=5)


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    memory_type: str
    content: str
    context: Optional[Dict[str, Any]] = None
    tags: List[str]
    importance: int
    created_at: datetime
    updated_at: datetime


class MemoryRecallQuery(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "What topics does user struggle with?"})
    tags: Optional[List[str]] = None
    top_k: int = Field(default=5, ge=1, le=20)
