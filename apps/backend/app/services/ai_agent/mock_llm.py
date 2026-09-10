"""
LLM provider for CircuitGPT.

Priority order:
  1. If GROQ_API_KEY is set → use ChatGroq (llama-3.3-70b-versatile by default).
  2. Otherwise → fall back to MockLLM (deterministic, zero-dependency).
"""

from typing import Any, Dict, List


class MockLLM:
    """Deterministic offline fallback — no API key required."""

    def generate_plan(self, query: str) -> List[str]:
        return [
            "Analyse the circuit query & identify the relevant EE principles",
            "Recall user memory profile for personalised learning context",
            "Query RAG vector store for textbook formulas & course materials",
            "Execute numerical solver for node voltages / phasor equations",
            "Format citations & synthesise step-by-step response",
        ]

    def generate_response(self, query: str, context: Dict[str, Any]) -> str:
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


def _build_groq_llm():
    """
    Attempt to build a real ChatGroq instance.
    Returns (groq_llm, True) on success, or (None, False) when the key is absent.
    """
    try:
        from app.core.config import settings
        from langchain_groq import ChatGroq

        if not settings.GROQ_API_KEY:
            return None, False

        llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.3,
            max_tokens=2048,
        )
        return llm, True
    except Exception:
        return None, False


class GroqLLM:
    """
    Thin wrapper around ChatGroq with MockLLM fallback.
    """

    def __init__(self) -> None:
        self._llm, self._live = _build_groq_llm()
        if self._live:
            print(f"[CircuitGPT] Using Groq LLM — model: {__import__('app.core.config', fromlist=['settings']).settings.GROQ_MODEL}")
        else:
            print("[CircuitGPT] Groq key not found — using MockLLM fallback.")
        self._mock = MockLLM()

    # ── Plan generation ─────────────────────────────────────────────

    def generate_plan(self, query: str) -> list:
        if not self._live:
            return self._mock.generate_plan(query)
        try:
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=(
                    "You are CircuitGPT, an expert Electrical Engineering tutor. "
                    "Given the student query, return ONLY a numbered list of 5 concise "
                    "solution steps. No preamble, no trailing text."
                )),
                HumanMessage(content=f"Query: {query}"),
            ]
            response = self._llm.invoke(messages)
            lines = [l.strip(" 1234567890.)") for l in response.content.strip().splitlines() if l.strip()]
            return [l for l in lines if l][:5] or self._mock.generate_plan(query)
        except Exception as e:
            print(f"[GroqLLM] plan error: {e}  — using mock")
            return self._mock.generate_plan(query)

    # ── Response generation ──────────────────────────────────────────

    def generate_response(self, query: str, context: Dict[str, Any]) -> str:
        if not self._live:
            return self._mock.generate_response(query, context)
        try:
            from langchain_core.messages import SystemMessage, HumanMessage

            docs_text = "\n".join(
                f"- [{d.get('doc_id','')}] {d.get('title','')}: {d.get('content','')}"
                for d in context.get("docs", [])
            )
            math_text = str(context.get("math", {}))
            citations = "; ".join(c.get("source", "") for c in context.get("citations", []))

            messages = [
                SystemMessage(content=(
                    "You are CircuitGPT, an expert EE tutor specialising in circuit analysis, "
                    "signal processing and electromagnetics. Give clear, step-by-step answers "
                    "with LaTeX equations where appropriate. Cite sources provided."
                )),
                HumanMessage(content=(
                    f"Student Question: {query}\n\n"
                    f"Retrieved Course Materials:\n{docs_text}\n\n"
                    f"Computed Results: {math_text}\n\n"
                    f"References: {citations}"
                )),
            ]
            response = self._llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"[GroqLLM] response error: {e}  — using mock")
            return self._mock.generate_response(query, context)
