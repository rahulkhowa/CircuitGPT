from typing import Any


class RerankerService:
    """
    Cross-encoder reranker for re-ordering retrieved RAG document chunks based on semantic relevance.
    """

    def rerank(self, query: str, documents: list[dict[str, Any]], top_k: int = 5) -> list[dict[str, Any]]:
        """
        Rerank document points by combining vector score with query token overlap.
        """
        query_words = set(query.lower().split())

        for doc in documents:
            payload = doc.get("payload", {})
            text = payload.get("text", "").lower()
            text_words = set(text.split())
            overlap = len(query_words.intersection(text_words)) / max(1, len(query_words))
            base_score = doc.get("score", 0.5)
            reranked_score = round(0.7 * base_score + 0.3 * overlap, 4)
            doc["rerank_score"] = reranked_score

        documents.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        return documents[:top_k]
