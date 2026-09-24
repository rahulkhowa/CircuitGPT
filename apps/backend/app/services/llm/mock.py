import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from app.services.llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic offline fallback provider when no active API key is set.
    """

    def generate_plan(self, query: str) -> list[str]:
        return [
            "Analyse the circuit query & identify the relevant EE principles",
            "Recall user memory profile for personalised learning context",
            "Query RAG vector store for textbook formulas & course materials",
            "Execute numerical solver for node voltages / phasor equations",
            "Format citations & synthesise step-by-step response",
        ]

    def generate_response(self, query: str, context: dict[str, Any]) -> str:
        docs = context.get("docs", [])
        math = context.get("math", {})
        citations = context.get("citations", [])

        doc_titles = ", ".join(d.get("title", "") for d in docs) or "Course Materials"
        vout = math.get("v2_volts", "calculated")
        refs = " | ".join(c.get("source", "") for c in citations) or doc_titles

        return (
            f"**CircuitGPT Analysis** — *{query}*\n\n"
            "### Solution\n"
            "1. **Apply KCL at each node**: `∑ Iₙ = 0`\n"
            "2. **Thevenin equivalent**: `Z_th = V_oc / I_sc`\n"
            f"3. **Result**: `V_out ≈ {vout} V`\n\n"
            f"> **References**: {refs}"
        )

    async def stream_response(self, query: str, context: dict[str, Any]) -> AsyncGenerator[str, None]:
        full_text = self.generate_response(query, context)
        # Yield in small chunks to simulate streaming behavior
        words = full_text.split(" ")
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            yield chunk
            await asyncio.sleep(0.02)
