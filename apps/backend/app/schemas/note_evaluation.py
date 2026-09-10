from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class NoteEvaluationSubmit(BaseModel):
    note_id: UUID
    status: str = Field(..., json_schema_extra={"example": "APPROVED"})
    technical_accuracy_score: float = Field(..., ge=0.0, le=10.0)
    completeness_score: float = Field(..., ge=0.0, le=10.0)
    clarity_score: float = Field(..., ge=0.0, le=10.0)
    feedback_comments: str = Field(..., json_schema_extra={"example": "Excellent explanation of Phasor Domain transformations."})
    suggested_improvements: List[str] = Field(default_factory=list)


class NoteEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    note_id: UUID
    evaluator_id: UUID
    status: str
    technical_accuracy_score: float
    completeness_score: float
    clarity_score: float
    overall_score: float
    feedback_comments: str
    suggested_improvements: List[str]
    created_at: datetime
    updated_at: datetime
