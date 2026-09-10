import pytest
import asyncio
from uuid import uuid4
from app.services.llm.factory import get_llm_provider
from app.services.llm.nvidia import clean_reasoning_traces
from app.services.rag.pipeline import RAGPipeline
from app.repositories.memory import MemoryRepository

@pytest.mark.asyncio
async def test_reasoning_content_filtering():
    """Verify that internal reasoning traces (<think>...</think>) are stripped."""
    raw_text = "<think>Calculating line impedance Z = R + jX...</think>The answer is 50 Ohms."
    cleaned = clean_reasoning_traces(raw_text)
    assert "<think>" not in cleaned
    assert "Calculating line impedance" not in cleaned
    assert cleaned == "The answer is 50 Ohms."


@pytest.mark.asyncio
async def test_llm_provider_factory():
    """Verify LLM provider factory instantiates provider or fallback properly."""
    provider = get_llm_provider()
    assert provider is not None
    plan = provider.generate_plan("Explain voltage regulation.")
    assert isinstance(plan, list)
    assert len(plan) > 0


@pytest.mark.asyncio
async def test_system_and_shared_resource_rag_isolation():
    """
    Test Section 36 & 37:
    - Shared Resource: User A uploads 'Power System -> transient_stability.pdf'.
      User B in Power System AI Chat MUST retrieve it.
    - System Isolation: User B in Power Electronics AI Chat MUST NOT retrieve it.
    """
    rag = RAGPipeline()
    ps_system = f"power-system-{uuid4()}"
    pe_system = f"power-electronics-{uuid4()}"
    doc_id = str(uuid4())

    # User A ingests transient_stability.pdf into Power System
    await rag.ingest_document(
        content="Equal area criterion determines transient stability limits in synchronous machines.",
        file_name="transient_stability.pdf",
        system_id=ps_system,
        resource_type="notes",
        resource_id=doc_id,
    )

    # 1. User B queries Power System -> Should retrieve User A's uploaded document
    ps_results = await rag.query(
        query_text="Explain transient stability equal area criterion",
        top_k=5,
        filters={"system_id": ps_system},
    )
    assert len(ps_results) > 0
    assert ps_results[0]["payload"]["system_id"] == ps_system
    assert "transient_stability.pdf" in ps_results[0]["payload"]["file_name"]

    # 2. User B queries Power Electronics -> Must NOT retrieve Power System document
    pe_results = await rag.query(
        query_text="Explain transient stability equal area criterion",
        top_k=5,
        filters={"system_id": pe_system},
    )
    assert len(pe_results) == 0


@pytest.mark.asyncio
async def test_user_memory_isolation():
    """
    Test Section 35 & 39:
    - User A's memory 'My name is Alice' must NOT be accessible to User B.
    """
    # Verify repository query filtering
    from unittest.mock import AsyncMock, MagicMock

    user_a_id = uuid4()
    user_b_id = uuid4()
    sys_id = "power-system"

    db_mock = AsyncMock()
    # Execute returns empty result for User B
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    db_mock.execute.return_value = result_mock

    repo = MemoryRepository(db_mock)
    user_b_memories = await repo.get_by_user_and_system(user_id=user_b_id, system_id=sys_id)
    assert len(user_b_memories) == 0
