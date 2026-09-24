from typing import Any

from app.services.ai_agent.state import AgentState


def citation_node(state: AgentState) -> dict[str, Any]:
    """
    Citation Node: Formats academic citations and course reference links.
    """
    docs = state.get("retrieved_docs", [])
    citations: list[dict[str, str]] = []
    for doc in docs:
        citations.append({
            "source": doc.get("title", "Course Note"),
            "ref": f"[{doc.get('doc_id')}]",
        })
    return {
        "citations": citations,
        "next_node": "generator",
    }
