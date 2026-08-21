"""Unit tests for Pydantic Settings and configuration logic."""

from app.core.config import Settings


def test_settings_defaults() -> None:
    """Verify default settings values when initialized."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/recover_ai",
        LOG_LEVEL="INFO",
    )
    assert settings.APP_NAME == "RecoverAI API"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert settings.PORT == 8000
    assert settings.DB_POOL_SIZE == 10
    assert settings.DB_MAX_OVERFLOW == 20
    assert settings.LOG_LEVEL == "INFO"


def test_cors_origins_parsing() -> None:
    """Verify comma-separated CORS allowed origins parses into a cleaned list."""
    settings = Settings(
        CORS_ALLOWED_ORIGINS="http://localhost:3000, https://app.recoverai.com , http://127.0.0.1:3000"
    )
    origins = settings.get_cors_origins()
    assert origins == [
        "http://localhost:3000",
        "https://app.recoverai.com",
        "http://127.0.0.1:3000",
    ]


def test_database_url_asyncpg_conversion() -> None:
    """Verify standard postgresql:// URI is automatically converted to postgresql+asyncpg://."""
    settings_standard = Settings(DATABASE_URL="postgresql://user:pass@localhost:5432/test_db")
    assert settings_standard.DATABASE_URL.startswith("postgresql+asyncpg://")

    settings_short = Settings(DATABASE_URL="postgres://user:pass@localhost:5432/test_db")
    assert settings_short.DATABASE_URL.startswith("postgresql+asyncpg://")


def test_environment_helpers() -> None:
    """Verify environment property helper methods."""
    prod_settings = Settings(APP_ENV="production")
    assert prod_settings.is_production is True
    assert prod_settings.is_development is False

    dev_settings = Settings(APP_ENV="development")
    assert dev_settings.is_development is True
    assert dev_settings.is_production is False
