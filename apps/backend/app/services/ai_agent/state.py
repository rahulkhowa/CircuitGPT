from typing import Any, TypedDict


class AgentState(TypedDict):
    """
    Shared state schema passed between nodes in the CircuitGPT LangGraph workflow.
    Ensures user_id and system_id isolation and context tracking.
    """
    user_id: str | None
    system_id: str | None
    messages: list[dict[str, str]]
    query: str
    plan: list[str]
    current_step: int
    retrieved_docs: list[dict[str, Any]]
    memory_context: list[dict[str, Any]]
    web_results: list[dict[str, Any]]
    math_results: dict[str, Any]
    citations: list[dict[str, str]]
    final_response: str
    next_node: str
