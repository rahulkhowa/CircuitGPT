import math
import hashlib
from typing import List


class EmbeddingService:
    """
    Embedding service for generating dense vector embeddings (384-dimensional).
    Uses a deterministic hashing vectorizer for zero-dependency test reliability and high-speed execution.
    """

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate a 384-dim unit-normalized float vector representation.
        """
        vector = [0.0] * self.dimension
        if not text:
            return vector

        # Deterministic feature projection from SHA-256 tokens
        words = text.lower().split()
        for word in words:
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            val = ((h >> 8) % 1000) / 1000.0 - 0.5
            vector[idx] += val

        # L2 Normalization
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.get_embedding(t) for t in texts]
