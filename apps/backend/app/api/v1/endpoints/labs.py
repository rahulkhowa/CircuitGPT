from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.lab import LabAssistantRequest, LabAssistantResponse
from app.services.lab_assistant import LabAssistantService

router = APIRouter()


@router.post("/troubleshoot", response_model=LabAssistantResponse, status_code=status.HTTP_200_OK)
async def troubleshoot_lab(
    payload: LabAssistantRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    AI Lab Assistant: Troubleshoot circuit wiring, oscilloscope settings, and measurement anomalies.
    """
    service = LabAssistantService(db)
    return await service.troubleshoot_experiment(payload)
