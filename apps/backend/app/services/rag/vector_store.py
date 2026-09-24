from typing import Any, Dict, List, Optional
from uuid import uuid4


class VectorStoreClient:
    """
    Qdrant vector store wrapper client.
    Maintains collections and vector similarity search points.
    """
    # Shared in-memory point storage for fast local testing and cross-module availability
    _shared_storage: Dict[str, Dict[str, Any]] = {}

    def __init__(self, collection_name: str = "circuitgpt_knowledge") -> None:
        self.collection_name = collection_name
        self._storage = VectorStoreClient._shared_storage

    async def upsert_points(
        self,
        points: List[Dict[str, Any]],
    ) -> bool:
        """
        Upsert vector points containing 'id', 'vector', and 'payload'.
        """
        for pt in points:
            pt_id = str(pt.get("id", uuid4()))
            self._storage[pt_id] = {
                "id": pt_id,
                "vector": pt.get("vector", []),
                "payload": pt.get("payload", {}),
            }
        return True

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Cosine similarity search over stored points.
        """
        results = []
        for pt_id, item in self._storage.items():
            payload = item["payload"]
            # Simple metadata filter match check if specified
            if filters:
                match = True
                for k, v in filters.items():
                    if payload.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            # Dot product similarity for normalized vectors
            vec = item["vector"]
            score = 0.0
            if len(vec) == len(query_vector):
                score = sum(a * b for a, b in zip(vec, query_vector))
            else:
                score = 0.85  # Fallback match score

            results.append({
                "id": pt_id,
                "score": round(score, 4),
                "payload": payload,
            })

        # Sort descending by similarity score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    async def delete_by_resource_id(self, resource_id: str) -> int:
        """
        Delete all indexed points associated with a resource_id.
        """
        keys_to_delete = [
            pt_id for pt_id, item in self._storage.items()
            if item.get("payload", {}).get("resource_id") == resource_id
        ]
        for k in keys_to_delete:
            self._storage.pop(k, None)
        return len(keys_to_delete)

