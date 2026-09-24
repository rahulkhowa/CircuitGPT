from typing import Any

from app.services.rag.doc_processor import DocumentProcessor
from app.services.rag.embeddings import EmbeddingService
from app.services.rag.reranker import RerankerService
from app.services.rag.vector_store import VectorStoreClient
from app.services.rag.video_processor import VideoProcessor


class RAGPipeline:
    """
    Unified System-Scoped RAG Pipeline:
    Combines Document Processing, Audio/Video Transcription, Embedding Generation,
    Vector Store Indexing, and Semantic Retrieval with Cross-Encoder Reranking.
    """

    def __init__(self) -> None:
        self.doc_processor = DocumentProcessor(chunk_size=300, chunk_overlap=30)
        self.embeddings = EmbeddingService(dimension=384)
        self.vector_store = VectorStoreClient(collection_name="circuitgpt_knowledge")
        self.reranker = RerankerService()
        self.video_processor = VideoProcessor()

    async def ingest_document(
        self,
        content: str,
        file_name: str,
        system_id: str,
        resource_type: str,
        resource_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process text content into chunks, compute embeddings, and index into Qdrant vector store
        scoped by system_id.
        """
        base_meta = {
            "system_id": system_id,
            "resource_id": resource_id,
            "resource_type": resource_type,
            "file_name": file_name,
            **(metadata or {}),
        }

        chunks = self.doc_processor.process_text(content, file_name, base_meta)
        points = []

        for chunk in chunks:
            vector = self.embeddings.get_embedding(chunk["text"])
            points.append({
                "id": chunk["chunk_id"],
                "vector": vector,
                "payload": {
                    "text": chunk["text"],
                    "chunk_index": chunk["chunk_index"],
                    "file_name": file_name,
                    "system_id": system_id,
                    "resource_id": resource_id,
                    "resource_type": resource_type,
                    **(metadata or {}),
                },
            })

        if points:
            await self.vector_store.upsert_points(points)

        return {
            "file_name": file_name,
            "system_id": system_id,
            "resource_id": resource_id,
            "total_chunks": len(chunks),
            "indexed": True,
        }

    async def ingest_video(
        self,
        video_filename: str,
        system_id: str,
        resource_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Extract audio, transcribe video with timestamps, and index into vector store.
        """
        transcription_res = await self.video_processor.process_video(video_filename)
        transcript = transcription_res.get("transcript", "")
        return await self.ingest_document(
            content=transcript,
            file_name=video_filename,
            system_id=system_id,
            resource_type="videos",
            resource_id=resource_id,
            metadata={
                "duration_seconds": transcription_res.get("duration_seconds", 0),
                **(metadata or {}),
            },
        )

    async def query(
        self, query_text: str, top_k: int = 5, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Vector search + Reranking retrieval pipeline filtered by system_id.
        """
        query_vector = self.embeddings.get_embedding(query_text)
        initial_results = await self.vector_store.search(
            query_vector=query_vector, top_k=top_k * 2, filters=filters
        )
        reranked_results = self.reranker.rerank(query_text, initial_results, top_k=top_k)
        return reranked_results

    async def delete_resource(self, resource_id: str) -> int:
        """
        Remove all vector chunks for a specific resource from the vector store.
        """
        return await self.vector_store.delete_by_resource_id(resource_id)

