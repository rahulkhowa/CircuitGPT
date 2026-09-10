import re
import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional
from openai import AsyncOpenAI, OpenAI

from app.core.config import settings
from app.services.llm.base import BaseLLMProvider


def clean_reasoning_traces(text: str) -> str:
    """
    Strips internal reasoning tags (<think>...</think>) or chain-of-thought blocks.
    Never exposes internal reasoning traces to the user interface.
    """
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"</?think>", "", cleaned)
    return cleaned.strip()


class NvidiaLLMProvider(BaseLLMProvider):
    """
    Official NVIDIA NIM OpenAI-compatible LLM Provider integration for Nemotron models.
    Supports reasoning_content handling, enable_thinking, and reasoning_budget.
    """

    def __init__(self) -> None:
        self.api_key = settings.NVIDIA_API_KEY
        self.base_url = settings.NVIDIA_BASE_URL
        self.model = settings.NVIDIA_MODEL
        self.reasoning_effort = settings.NVIDIA_REASONING_EFFORT
        self.max_tokens = settings.NVIDIA_MAX_TOKENS
        self.temperature = settings.NVIDIA_TEMPERATURE
        self.top_p = settings.NVIDIA_TOP_P

        self._client = OpenAI(base_url=self.base_url, api_key=self.api_key or "invalid")
        self._async_client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key or "invalid")

    def _build_extra_body(self) -> Dict[str, Any]:
        """Construct extra_body for official Nemotron reasoning parameters."""
        extra = {}
        enable_thinking = self.reasoning_effort != "none"
        extra["chat_template_kwargs"] = {"enable_thinking": enable_thinking}
        return extra

    def generate_plan(self, query: str) -> List[str]:
        if not self.api_key:
            from app.services.llm.mock import MockLLMProvider
            return MockLLMProvider().generate_plan(query)

        system_msg = (
            "You are CircuitGPT, an expert Electrical Engineering tutor. "
            "Given the student query, return ONLY a numbered list of 5 concise "
            "solution steps. No preamble, no trailing text, no internal reasoning output."
        )
        try:
            try:
                res = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": query},
                    ],
                    temperature=0.2,
                    max_tokens=512,
                    extra_body=self._build_extra_body(),
                )
            except Exception:
                # Retry without extra_body if unsupported
                res = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": query},
                    ],
                    temperature=0.2,
                    max_tokens=512,
                )
            raw_content = res.choices[0].message.content or ""
            cleaned = clean_reasoning_traces(raw_content)
            lines = [l.strip(" 1234567890.)-") for l in cleaned.splitlines() if l.strip()]
            return [l for l in lines if l][:5] or ["Formulate problem statement", "Apply KCL/KVL", "Solve system", "Verify", "Output result"]
        except Exception as exc:
            print(f"[NvidiaLLMProvider] Plan error: {exc}")
            from app.services.llm.mock import MockLLMProvider
            return MockLLMProvider().generate_plan(query)

    def generate_response(self, query: str, context: Dict[str, Any]) -> str:
        if not self.api_key:
            from app.services.llm.mock import MockLLMProvider
            return MockLLMProvider().generate_response(query, context)

        docs_text = "\n".join(
            f"- [{d.get('title','Doc')}] {d.get('content','')}"
            for d in context.get("docs", [])
        )
        memories_text = "\n".join(
            f"- {m.get('key','')}: {m.get('value','')}"
            for m in context.get("memories", [])
        )
        citations_text = "; ".join(c.get("source", "") for c in context.get("citations", []))

        system_prompt = context.get("system_prompt") or (
            "You are CircuitGPT, an expert Electrical Engineering tutor. "
            "Explain concepts and step-by-step calculations in simple, clean, and natural English. "
            "Do NOT use complex or raw LaTeX markup (e.g. avoid \\frac, \\sum, \\cdot); use clean, readable plain-text notation (e.g. I1 = 1000 / 120 = 8.33 A, 8.33∠0° A). "
            "Do NOT include internal reasoning traces or <think> tags in your answer."
        )

        user_content = (
            f"Query: {query}\n\n"
            f"Student Memory Profile:\n{memories_text}\n\n"
            f"Retrieved Course Materials:\n{docs_text}\n\n"
            f"Citations: {citations_text}"
        )

        try:
            try:
                res = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_tokens,
                    extra_body=self._build_extra_body(),
                )
            except Exception:
                res = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_tokens,
                )
            content = res.choices[0].message.content or ""
            return clean_reasoning_traces(content)
        except Exception as exc:
            print(f"[NvidiaLLMProvider] Generate error: {exc}")
            from app.services.llm.mock import MockLLMProvider
            return MockLLMProvider().generate_response(query, context)

    async def stream_response(self, query: str, context: Dict[str, Any]) -> AsyncGenerator[str, None]:
        if not self.api_key:
            from app.services.llm.mock import MockLLMProvider
            async for chunk in MockLLMProvider().stream_response(query, context):
                yield chunk
            return

        docs_text = "\n".join(
            f"- [{d.get('title','Doc')}] {d.get('content','')}"
            for d in context.get("docs", [])
        )
        memories_text = "\n".join(
            f"- {m.get('key','')}: {m.get('value','')}"
            for m in context.get("memories", [])
        )
        citations_text = "; ".join(c.get("source", "") for c in context.get("citations", []))

        system_prompt = context.get("system_prompt") or (
            "You are CircuitGPT, an expert Electrical Engineering tutor. "
            "Provide accurate, clear step-by-step mathematical solutions with LaTeX equations where appropriate. "
            "Do NOT include internal reasoning traces or <think> tags in your answer."
        )

        user_content = (
            f"Query: {query}\n\n"
            f"Student Memory Profile:\n{memories_text}\n\n"
            f"Retrieved Course Materials:\n{docs_text}\n\n"
            f"Citations: {citations_text}"
        )

        try:
            try:
                stream = await self._async_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_tokens,
                    stream=True,
                    extra_body=self._build_extra_body(),
                )
            except Exception:
                stream = await self._async_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_tokens,
                    stream=True,
                )

            inside_think_tag = False
            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta

                # Separate reasoning_content field returned by NVIDIA NIM API is ignored
                # so raw reasoning traces are NOT shown in user UI
                reasoning = getattr(delta, "reasoning_content", None)
                if reasoning:
                    pass  # Processed separately or hidden per Section 5 of Update.md

                content = getattr(delta, "content", None) or ""

                if "<think>" in content:
                    inside_think_tag = True
                    continue
                if "</think>" in content:
                    inside_think_tag = False
                    content = content.split("</think>")[-1]

                if not inside_think_tag and content:
                    yield content

        except Exception as exc:
            print(f"[NvidiaLLMProvider] Streaming error: {exc}")
            from app.services.llm.mock import MockLLMProvider
            async for chunk in MockLLMProvider().stream_response(query, context):
                yield chunk
