from typing import Any, Dict, List
from app.services.ai_agent.state import AgentState


def memory_node(state: AgentState) -> Dict[str, Any]:
    """
    Memory Node: Recalls user learning preferences and prior misconceptions.
    """
    memory_context: List[Dict[str, Any]] = [
        {
            "type": "mastery",
            "key": "KCL_understanding",
            "content": "User has mastered basic KCL; prefers step-by-step mathematical steps.",
        },
        {
            "type": "weakness",
            "key": "Phasor_domain",
            "content": "User needs reminders on converting sine to cosine phasors.",
        },
    ]
    return {
        "memory_context": memory_context,
        "next_node": "retriever",
    }
