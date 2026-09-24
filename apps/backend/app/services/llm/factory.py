from app.core.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.mock import MockLLMProvider
from app.services.llm.nvidia import NvidiaLLMProvider


def get_llm_provider() -> BaseLLMProvider:
    """
    Factory function returning active LLM provider instance based on settings.LLM_PROVIDER.
    Falls back gracefully to MockLLMProvider if API keys are missing or invalid.
    """
    provider_name = (settings.LLM_PROVIDER or "nvidia").lower().strip()

    if provider_name == "nvidia":
        if settings.NVIDIA_API_KEY:
            return NvidiaLLMProvider()
        else:
            print("[CircuitGPT] LLM_PROVIDER is nvidia but NVIDIA_API_KEY is not set. Using MockLLMProvider fallback.")
            return MockLLMProvider()

    # Add future providers here (e.g., groq, openai, anthropic)
    return MockLLMProvider()
