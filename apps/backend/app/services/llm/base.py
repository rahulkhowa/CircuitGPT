from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers in CircuitGPT.
    Ensures decoupled model invocation and streaming across agents and endpoints.
    """

    @abstractmethod
    def generate_plan(self, query: str) -> list[str]:
        """Generate execution steps for query."""
        pass

    @abstractmethod
    def generate_response(self, query: str, context: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def stream_response(self, query: str, context: dict[str, Any]) -> AsyncGenerator[str, None]:
        """Yield response tokens chunk-by-chunk without exposing internal reasoning."""
        pass
