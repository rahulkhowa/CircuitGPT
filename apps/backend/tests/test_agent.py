import pytest
from app.services.ai_agent.graph import circuit_agent_graph

def test_langgraph_agent_structure():
    assert circuit_agent_graph is not None
    nodes = list(circuit_agent_graph.nodes.keys())
    expected_nodes = ["planner", "memory", "retriever", "search", "math", "citation", "generator"]
    for node in expected_nodes:
        assert node in nodes
