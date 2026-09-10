from typing import Any, Dict, List, Optional
from uuid import uuid4


class DocumentChunk(Dict[str, Any]):
    chunk_id: str
    text: str
    chunk_index: int
    metadata: Dict[str, Any]


class DocumentProcessor:
    """
    Document Processor for parsing PDF, Markdown, and TXT files into semantic chunks.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_text(self, text: str, file_name: str, extra_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Splits text string into overlapping chunks.
        """
        words = text.split()
        chunks: List[Dict[str, Any]] = []

        if not words:
            return chunks

        stride = max(1, self.chunk_size - self.chunk_overlap)
        index = 0
        for i in range(0, len(words), stride):
            chunk_words = words[i : i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            chunk_id = str(uuid4())
            meta = {
                "file_name": file_name,
                "word_count": len(chunk_words),
                "start_word": i,
                **(extra_metadata or {}),
            }
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "chunk_index": index,
                    "metadata": meta,
                }
            )
            index += 1
        return chunks
