from typing import Any

from app.services.ai_agent.state import AgentState
from app.services.llm.factory import get_llm_provider


def generator_node(state: AgentState) -> dict[str, Any]:
    """
    Generator Node: Synthesizes final response using the active LLM provider.
    """
    query = state.get("query", "")
    context = {
        "docs": state.get("retrieved_docs", []),
        "memories": state.get("memory_context", []),
        "math": state.get("math_results", {}),
        "citations": state.get("citations", []),
    }
    llm = get_llm_provider()
    response = llm.generate_response(query, context)
    return {
        "final_response": response,
        "next_node": "END",
    }
