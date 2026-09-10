from typing import List
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.quiz import (
    QuizCreate,
    QuizResponse,
    QuizAttemptSubmit,
    QuizAttemptResponse,
)
from app.services.quiz import QuizService

router = APIRouter()


@router.post("", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    payload: QuizCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate or create a new interactive quiz.
    """
    service = QuizService(db)
    return await service.create_quiz(payload)


@router.post("/submit", response_model=QuizAttemptResponse)
async def submit_quiz_attempt(
    payload: QuizAttemptSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit user quiz answers and receive instant auto-graded results.
    """
    service = QuizService(db)
    return await service.grade_attempt(current_user.id, payload)
