from typing import Any

from app.services.ai_agent.state import AgentState


def search_node(state: AgentState) -> dict[str, Any]:
    """
    Search Node: Performs external web search for datasheets and latest EE references.
    """
    _query = state.get("query", "")  # noqa: F841 — reserved for future web search integration
    web_results: list[dict[str, Any]] = [
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
