from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.note_evaluation import NoteEvaluationSubmit, NoteEvaluationResponse


class NoteEvaluatorService:
    """
    AI & Faculty Note Evaluation service for reviewing, scoring, and approving student lecture notes.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def evaluate_note(self, evaluator_id: UUID, payload: NoteEvaluationSubmit) -> NoteEvaluationResponse:
        overall = round(
            (payload.technical_accuracy_score + payload.completeness_score + payload.clarity_score) / 3.0, 2
        )

        return NoteEvaluationResponse(
            id=uuid4(),
            note_id=payload.note_id,
            evaluator_id=evaluator_id,
            status=payload.status,
            technical_accuracy_score=payload.technical_accuracy_score,
            completeness_score=payload.completeness_score,
            clarity_score=payload.clarity_score,
            overall_score=overall,
            feedback_comments=payload.feedback_comments,
            suggested_improvements=payload.suggested_improvements,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
