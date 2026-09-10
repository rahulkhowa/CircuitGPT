from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict):
    """
    Shared state schema passed between nodes in the CircuitGPT LangGraph workflow.
    Ensures user_id and system_id isolation and context tracking.
    """
    user_id: Optional[str]
    system_id: Optional[str]
    messages: List[Dict[str, str]]
    query: str
    plan: List[str]
    current_step: int
    retrieved_docs: List[Dict[str, Any]]
    memory_context: List[Dict[str, Any]]
    web_results: List[Dict[str, Any]]
    math_results: Dict[str, Any]
    citations: List[Dict[str, str]]
    final_response: str
    next_node: str
