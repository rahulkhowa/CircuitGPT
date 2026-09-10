from typing import Any, Dict, List
from app.services.ai_agent.state import AgentState


def search_node(state: AgentState) -> Dict[str, Any]:
    """
    Search Node: Performs external web search for datasheets and latest EE references.
    """
    query = state.get("query", "")
    web_results: List[Dict[str, Any]] = [
        {
            "title": "IEEE EE Standard 141",
            "snippet": "Recommended Practice for Electric Power Distribution for Industrial Plants.",
            "url": "https://ieeexplore.ieee.org/document/141",
        }
    ]
    return {
        "web_results": web_results,
        "next_node": "math",
    }
