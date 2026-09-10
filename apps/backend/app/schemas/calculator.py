from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CalculatorType(str, Enum):
    OHMS_LAW = "OHMS_LAW"
    IMPEDANCE = "IMPEDANCE"
    FILTER_DESIGN = "FILTER_DESIGN"
    RLC_TRANSIENT = "RLC_TRANSIENT"
    THREE_PHASE = "THREE_PHASE"
    TRANSFORMER = "TRANSFORMER"


class EECalculatorRequest(BaseModel):
    calculation_type: CalculatorType
    inputs: Dict[str, float] = Field(..., json_schema_extra={"example": {"R": 1000.0, "C": 1e-6, "vin": 5.0}})


class EECalculatorResponse(BaseModel):
    calculation_type: CalculatorType
    results: Dict[str, float] = Field(..., json_schema_extra={"example": {"fc_hz": 159.15, "w_rad": 1000.0}})
    formula_used: str = Field(..., json_schema_extra={"example": "fc = 1 / (2 * pi * R * C)"})
    step_by_step_explanation: List[str] = Field(default_factory=list)
