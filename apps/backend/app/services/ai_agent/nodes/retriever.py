import asyncio
from typing import Any, Dict, List
from app.services.ai_agent.state import AgentState
from app.services.rag.pipeline import RAGPipeline
from app.core.config import settings

rag_pipeline = RAGPipeline()


def retriever_node(state: AgentState) -> Dict[str, Any]:
    """
    Retriever Node: Fetches vector embeddings from Qdrant vector store scoped by system_id.
    """
    query = state.get("query", "")
    system_id = state.get("system_id")

    filters = {}
    if system_id:
        filters["system_id"] = system_id

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Run in event loop if already present
            import nest_asyncio
            nest_asyncio.apply()
            results = loop.run_until_complete(
                rag_pipeline.query(query, top_k=settings.AI_RAG_TOP_K, filters=filters if filters else None)
            )
        else:
            results = asyncio.run(
                rag_pipeline.query(query, top_k=settings.AI_RAG_TOP_K, filters=filters if filters else None)
            )
    except Exception:
        results = []

    retrieved_docs = []
    for item in results:
        payload = item.get("payload", {})
        retrieved_docs.append({
            "doc_id": item.get("id"),
            "title": payload.get("file_name", "Document"),
            "content": payload.get("text", ""),
            "score": item.get("score", 0.0),
        })

    return {
        "retrieved_docs": retrieved_docs,
        "next_node": "search",
    }
