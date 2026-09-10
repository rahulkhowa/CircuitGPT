from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers in CircuitGPT.
    Ensures decoupled model invocation and streaming across agents and endpoints.
    """

    @abstractmethod
    def generate_plan(self, query: str) -> List[str]:
        """Generate execution steps for query."""
        pass

    @abstractmethod
    def generate_response(self, query: str, context: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def stream_response(self, query: str, context: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Yield response tokens chunk-by-chunk without exposing internal reasoning."""
        pass
