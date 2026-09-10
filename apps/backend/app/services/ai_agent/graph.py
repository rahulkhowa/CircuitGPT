from langgraph.graph import StateGraph, END
from app.services.ai_agent.state import AgentState
from app.services.ai_agent.nodes import (
    planner_node,
    memory_node,
    retriever_node,
    search_node,
    math_node,
    citation_node,
    generator_node,
)


def create_agent_graph():
    """
    Constructs and compiles the 7-node CircuitGPT LangGraph workflow graph.
    """
    workflow = StateGraph(AgentState)

    # 1. Register Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("memory", memory_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("search", search_node)
    workflow.add_node("math", math_node)
    workflow.add_node("citation", citation_node)
    workflow.add_node("generator", generator_node)

    # 2. Set Entry Point
    workflow.set_entry_point("planner")

    # 3. Connect Direct & Sequential Edges
    workflow.add_edge("planner", "memory")
    workflow.add_edge("memory", "retriever")
    workflow.add_edge("retriever", "search")
    workflow.add_edge("search", "math")
    workflow.add_edge("math", "citation")
    workflow.add_edge("citation", "generator")
    workflow.add_edge("generator", END)

    return workflow.compile()


# Compiled agent graph instance
circuit_agent_graph = create_agent_graph()
