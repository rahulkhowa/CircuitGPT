from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.calculator import EECalculatorRequest, EECalculatorResponse
from app.services.ee_calculator import EECalculatorService

router = APIRouter()


@router.post("/calculate", response_model=EECalculatorResponse, status_code=status.HTTP_200_OK)
async def calculate_ee_formula(
    payload: EECalculatorRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    EE Calculator: Solve electrical equations (Ohm's Law, RLC resonance, Filter cutoffs, 3-Phase power).
    """
    service = EECalculatorService(db)
    return await service.calculate(payload)
