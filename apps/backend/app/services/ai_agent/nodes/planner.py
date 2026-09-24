from typing import Any

from app.services.ai_agent.state import AgentState
from app.services.llm.factory import get_llm_provider


def planner_node(state: AgentState) -> dict[str, Any]:
    """
    Planner Node: Deconstructs the query into actionable execution steps using the active LLM provider.
    """
    query = state.get("query", "")
    llm = get_llm_provider()
    plan = llm.generate_plan(query)
    return {
        "plan": plan,
        "current_step": 1,
        "next_node": "memory",
    }
