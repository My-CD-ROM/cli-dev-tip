from __future__ import annotations

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstract base for AI tip providers."""

    @abstractmethod
    def generate_tips(self, topic: str | None, level: str | None, count: int) -> list[dict]:
        """Generate a batch of tips via an AI API."""


def create_provider(name: str, api_key: str, model: str | None = None) -> AIProvider:
    """Factory: create a provider by name with lazy SDK imports."""
    if name == "gemini":
        from dev_tip.ai.gemini import GeminiProvider

        return GeminiProvider(api_key, model=model)

    if name == "openrouter":
        from dev_tip.ai.openrouter import OpenRouterProvider

        return OpenRouterProvider(api_key, model=model)

    raise ValueError(f"Unknown AI provider: {name!r}")
