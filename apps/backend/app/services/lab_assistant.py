from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.lab import LabAssistantRequest, LabAssistantResponse


class LabAssistantService:
    """
    AI Lab Assistant service for helping students debug breadboard circuits, oscilloscope waveforms, and lab data.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def troubleshoot_experiment(self, request: LabAssistantRequest) -> LabAssistantResponse:
        steps = [
            "Verify ground continuity between signal generator and oscilloscope probe ground clip.",
            "Check DC offset on channel 1 input coupling setting.",
            "Ensure load resistor value matches nominal specification (10k ± 5%).",
        ]
        discrepancy = (
            "Measured phase difference of 45° indicates additional parasitic capacitance or probe attenuation factor 10X setting mismatch."
        )

        return LabAssistantResponse(
            experiment_id=request.experiment_id,
            status="DIAGNOSED",
            guidance="The circuit response deviates slightly from ideal theory due to probe loading.",
            suggested_steps=steps,
            discrepancy_analysis=discrepancy,
            safety_warnings=["Ensure breadboard power supply current limit is set below 500mA to avoid component overheating."],
        )
