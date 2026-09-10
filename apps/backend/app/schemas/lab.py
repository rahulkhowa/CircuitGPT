from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class LabOscilloscopeConfig(BaseModel):
    ch1_volts_per_div: float = Field(default=1.0, json_schema_extra={"example": 1.0})
    ch2_volts_per_div: float = Field(default=1.0, json_schema_extra={"example": 1.0})
    time_base_sec_per_div: float = Field(default=0.001, json_schema_extra={"example": 0.001})
    coupling: str = Field(default="DC", json_schema_extra={"example": "DC"})


class LabMeasurement(BaseModel):
    parameter: str = Field(..., json_schema_extra={"example": "V_pp"})
    theoretical_value: float = Field(..., json_schema_extra={"example": 5.0})
    measured_value: float = Field(..., json_schema_extra={"example": 4.82})
    unit: str = Field(..., json_schema_extra={"example": "V"})


class LabAssistantRequest(BaseModel):
    experiment_id: str = Field(..., json_schema_extra={"example": "lab-3-oscilloscope"})
    user_query: Optional[str] = Field(None, json_schema_extra={"example": "Why is the phase shift 45 degrees instead of 90 degrees?"})
    oscilloscope_config: Optional[LabOscilloscopeConfig] = None
    measurements: List[LabMeasurement] = Field(default_factory=list)


class LabAssistantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    experiment_id: str
    status: str = Field(..., json_schema_extra={"example": "DIAGNOSED"})
    guidance: str
    suggested_steps: List[str]
    discrepancy_analysis: Optional[str] = None
    safety_warnings: List[str] = Field(default_factory=list)
