from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class SimulationType(str, Enum):
    DC = "DC"
    AC = "AC"
    TRANSIENT = "TRANSIENT"
    OPERATING_POINT = "OPERATING_POINT"


class CircuitComponent(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "R1"})
    component_type: str = Field(..., json_schema_extra={"example": "Resistor"})
    nodes: List[str] = Field(..., json_schema_extra={"example": ["1", "0"]})
    value: float = Field(..., json_schema_extra={"example": 1000.0})
    unit: str = Field(..., json_schema_extra={"example": "Ohm"})
    parameters: Optional[Dict[str, Any]] = None


class NodeVoltage(BaseModel):
    node: str
    v_real: float
    v_imag: Optional[float] = 0.0
    magnitude: float
    phase_deg: Optional[float] = 0.0


class WaveformDataPoint(BaseModel):
    time_s: float
    node_voltages: Dict[str, float]
    branch_currents: Optional[Dict[str, float]] = None


class CircuitSimulationRequest(BaseModel):
    netlist: str = Field(..., json_schema_extra={"example": "V1 1 0 10\nR1 1 2 1k\nR2 2 0 2k\n.op"})
    simulation_type: SimulationType = SimulationType.DC
    transient_stop_s: Optional[float] = Field(None, json_schema_extra={"example": 0.01})
    transient_step_s: Optional[float] = Field(None, json_schema_extra={"example": 0.0001})
    ac_start_freq_hz: Optional[float] = Field(None, json_schema_extra={"example": 10.0})
    ac_stop_freq_hz: Optional[float] = Field(None, json_schema_extra={"example": 1000000.0})


class CircuitSimulationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    status: str = Field(..., json_schema_extra={"example": "SUCCESS"})
    execution_time_ms: float
    nodes: List[str]
    node_voltages: List[NodeVoltage]
    waveform: Optional[List[WaveformDataPoint]] = None
    netlist_summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
