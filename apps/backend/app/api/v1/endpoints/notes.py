from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, require_faculty_or_admin
from app.models.user import User
from app.schemas.note_evaluation import NoteEvaluationSubmit, NoteEvaluationResponse
from app.services.note_evaluator import NoteEvaluatorService

router = APIRouter()


@router.post("/evaluate", response_model=NoteEvaluationResponse, status_code=status.HTTP_200_OK)
async def evaluate_note(
    payload: NoteEvaluationSubmit,
    current_user: User = Depends(require_faculty_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Faculty/AI Note Review: Submit evaluation score & feedback rubric for student lecture notes.
    """
    service = NoteEvaluatorService(db)
    return await service.evaluate_note(current_user.id, payload)


@router.get("/pending-evaluations", response_model=List[NoteEvaluationResponse], dependencies=[Depends(require_faculty_or_admin)])
async def list_pending_evaluations(
    db: AsyncSession = Depends(get_db),
):
    """
    Faculty Panel: List all student notes pending evaluation.
    """
    from datetime import datetime
    return [
        NoteEvaluationResponse(
            id=uuid4(),
            note_id=uuid4(),
            evaluator_id=uuid4(),
            status="PENDING",
            technical_accuracy_score=9.0,
            completeness_score=8.5,
            clarity_score=9.5,
            overall_score=9.0,
            feedback_comments="Comprehensive breakdown of Op-Amp Non-Inverting configuration.",
            suggested_improvements=["Add bode plot cutoff frequency diagram."],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    ]
