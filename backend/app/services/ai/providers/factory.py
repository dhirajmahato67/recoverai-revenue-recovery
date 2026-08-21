"""Factory for instantiating AI providers based on application configuration."""

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.services.ai.providers.base import AIProvider
from app.services.ai.providers.mock_provider import MockProvider
from app.services.ai.providers.openai_provider import OpenAIProvider

logger = get_logger("app.services.ai.factory")


def get_ai_provider(settings: Settings | None = None) -> AIProvider:
    """Instantiate and return the configured AIProvider implementation."""
    cfg = settings or get_settings()
    provider_type = (cfg.AI_PROVIDER or "mock").lower().strip()

    if provider_type == "openai" and cfg.AI_API_KEY:
        logger.info(f"Initializing OpenAI Provider with model '{cfg.AI_MODEL}'")
        return OpenAIProvider(
            api_key=cfg.AI_API_KEY,
            model=cfg.AI_MODEL,
            timeout_seconds=cfg.AI_TIMEOUT_SECONDS,
        )

    # Fallback to deterministic mock provider for demo/offline/testing mode
    logger.info(f"Using deterministic MockProvider (mode={provider_type}, model={cfg.AI_MODEL})")
    return MockProvider(
        model=cfg.AI_MODEL,
        timeout_seconds=cfg.AI_TIMEOUT_SECONDS,
    )
