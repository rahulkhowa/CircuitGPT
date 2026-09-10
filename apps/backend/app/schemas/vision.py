from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class AnalysisType(str, Enum):
    OCR = "OCR"
    COMPONENT_DETECTION = "COMPONENT_DETECTION"
    NETLIST_EXTRACTION = "NETLIST_EXTRACTION"
    FULL_DIAGNOSIS = "FULL_DIAGNOSIS"


class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float


class DetectedComponent(BaseModel):
    label: str = Field(..., json_schema_extra={"example": "Resistor"})
    confidence: float = Field(..., json_schema_extra={"example": 0.95})
    bbox: BoundingBox
    pins: List[str] = Field(default_factory=list)
    detected_value: Optional[str] = Field(None, json_schema_extra={"example": "10k"})


class VisionAnalysisRequest(BaseModel):
    image_url: str = Field(..., json_schema_extra={"example": "https://storage.circuitgpt.io/schematics/circuit1.png"})
    analysis_type: AnalysisType = AnalysisType.NETLIST_EXTRACTION
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class VisionAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    image_url: str
    analysis_type: AnalysisType
    detected_components: List[DetectedComponent]
    generated_netlist: Optional[str] = None
    ocr_extracted_text: Optional[str] = None
    confidence_score: float
    processed_image_url: Optional[str] = None
