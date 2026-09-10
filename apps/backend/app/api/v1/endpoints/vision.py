from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.vision import VisionAnalysisRequest, VisionAnalysisResponse
from app.services.vision import VisionService

router = APIRouter()


@router.post("/analyze", response_model=VisionAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_schematic_image(
    payload: VisionAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Computer Vision: Extract components, OCR values, and netlist representation from schematic images.
    """
    service = VisionService(db)
    return await service.analyze_schematic(payload)
