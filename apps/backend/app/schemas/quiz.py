from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class QuizOption(BaseModel):
    id: str = Field(..., json_schema_extra={"example": "opt-a"})
    text: str = Field(..., json_schema_extra={"example": "10 Volts"})
    explanation: Optional[str] = None


class QuizQuestionCreate(BaseModel):
    question_text: str = Field(..., json_schema_extra={"example": "What is the voltage across R2 in a voltage divider with V_in=12V, R1=2k, R2=4k?"})
    options: List[QuizOption]
    correct_option_id: str = Field(..., json_schema_extra={"example": "opt-b"})
    explanation: str = Field(..., json_schema_extra={"example": "V_out = V_in * (R2 / (R1 + R2)) = 12 * (4/6) = 8V"})
    difficulty: str = Field(default="medium", json_schema_extra={"example": "medium"})


class QuizQuestionResponse(BaseModel):
    id: UUID
    question_text: str
    options: List[QuizOption]
    difficulty: str


class QuizCreate(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Voltage Dividers & KCL Practice Quiz"})
    subject_id: str = Field(..., json_schema_extra={"example": "ee101"})
    module_id: Optional[str] = Field(None, json_schema_extra={"example": "mod-1"})
    time_limit_minutes: int = Field(default=15, ge=1)
    questions: List[QuizQuestionCreate]


class QuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    subject_id: str
    module_id: Optional[str]
    time_limit_minutes: int
    total_questions: int
    created_at: datetime


class QuizAttemptSubmit(BaseModel):
    quiz_id: UUID
    user_answers: Dict[str, str] = Field(..., json_schema_extra={"example": {"q-1": "opt-b", "q-2": "opt-a"}})


class QuizAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    quiz_id: UUID
    user_id: UUID
    score: int
    total_questions: int
    percentage: float
    passed: bool
    detailed_feedback: Dict[str, Any] = Field(default_factory=dict)
    submitted_at: datetime
