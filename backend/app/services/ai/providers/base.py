"""Base AI Provider interface and data representations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AIProviderResult:
    """Standardized output structure returned by all AI providers."""

    text: str
    provider: str
    model: str
    latency_ms: int
    token_usage: dict[str, int] = field(default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
    raw_payload: Optional[dict[str, Any]] = None


class AIProvider(ABC):
    """Abstract provider defining contract for natural language completion backends."""

    def __init__(self, model: str, timeout_seconds: float = 15.0):
        self.model = model
        self.timeout_seconds = timeout_seconds

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name identifier of this AI provider backend."""
        pass

    @abstractmethod
    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        context: dict[str, Any],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> AIProviderResult:
        """Generate a natural language response grounded in the provided context dictionary."""
        pass
