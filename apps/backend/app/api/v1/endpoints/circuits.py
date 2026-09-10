from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.circuit import CircuitSimulationRequest, CircuitSimulationResponse
from app.services.circuit import CircuitSimulationService

router = APIRouter()


@router.post("/simulate", response_model=CircuitSimulationResponse, status_code=status.HTTP_200_OK)
async def simulate_circuit(
    payload: CircuitSimulationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Parse SPICE netlist and run AC/DC/Transient circuit simulation.
    """
    service = CircuitSimulationService(db)
    return await service.simulate(payload)


@router.get("/examples", response_model=List[Dict[str, Any]])
async def get_circuit_examples():
    """
    Fetch pre-loaded EE benchmark circuit netlists.
    """
    return [
        {
            "id": "ex-kcl",
            "name": "Nodal Analysis KCL Circuit",
            "subject_id": "ee101",
            "netlist": "V1 1 0 12\nR1 1 2 2k\nR2 2 0 4k\n.op",
        },
        {
            "id": "ex-rlc",
            "name": "Second-Order RLC Step Response",
            "subject_id": "ee101",
            "netlist": "V1 1 0 5\nR1 1 2 10\nL1 2 3 10m\nC1 3 0 1u\n.tran 100u 10m",
        },
    ]
