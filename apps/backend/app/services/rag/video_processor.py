from typing import Any
from uuid import uuid4


class VideoProcessor:
    """
    Video processor for converting video lecture transcripts and timestamped subtitles into RAG chunks.
    """

    def process_transcript(
        self, transcript_segments: list[dict[str, Any]], video_title: str
    ) -> list[dict[str, Any]]:
        chunks: list[dict[str, Any]] = []
        for idx, seg in enumerate(transcript_segments):
            chunk_id = str(uuid4())
            chunks.append({
                "chunk_id": chunk_id,
                "text": seg.get("text", ""),
                "chunk_index": idx,
                "metadata": {
                    "video_title": video_title,
                    "start_time": seg.get("start_time", 0.0),
                    "end_time": seg.get("end_time", 0.0),
                    "type": "video_transcript",
                },
            })
        return chunks
