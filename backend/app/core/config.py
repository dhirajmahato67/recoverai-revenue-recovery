"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized, type-safe application settings loaded from environment variables."""

    # Application Metadata
    APP_NAME: str = Field(default="RecoverAI API", description="Name of the application service")
    APP_ENV: Literal["development", "staging", "production", "testing"] = Field(
        default="development", description="Operational deployment environment"
    )
    DEBUG: bool = Field(default=False, description="Debug mode flag")
    API_V1_PREFIX: str = Field(default="/api/v1", description="Prefix for Version 1 API endpoints")
    HOST: str = Field(default="0.0.0.0", description="Host address to bind server")
    PORT: int = Field(default=8000, description="Port number to bind server")

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/recover_ai",
        description="Async SQLAlchemy database connection URI",
    )
    DB_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Max overflow connections allowed in pool")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Seconds to wait before timing out on getting a connection")
    DB_POOL_RECYCLE: int = Field(default=1800, description="Seconds after which connection is recycled")
    DB_ECHO: bool = Field(default=False, description="Echo raw SQL statements to logger")

    # CORS Configuration
    CORS_ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Comma-separated origins permitted for Cross-Origin Resource Sharing",
    )

    # Logging Configuration
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Log level verbosity"
    )

    # OpenAPI & Swagger UI
    DOCS_ENABLED: bool = Field(default=True, description="Enable Swagger UI and OpenAPI documentation")

    # Phase 4: Synthetic Pipeline & Risk Detection Configuration
    TRANSACTION_BATCH_SIZE: int = Field(default=500, description="Default batch size for bulk transaction ingestion")
    RISK_DEGRADATION_THRESHOLD: float = Field(default=0.05, description="Success rate drop threshold (delta fraction) to trigger risk signal")
    RISK_FAILURE_SPIKE_THRESHOLD: float = Field(default=0.10, description="Overall failure spike threshold to trigger risk signal")
    RISK_VELOCITY_THRESHOLD: int = Field(default=50, description="Threshold for failures in window to trigger velocity risk signal")
    BASELINE_WINDOW_MINUTES: int = Field(default=1440, description="Minutes for baseline historical comparison (default 24h)")
    CURRENT_WINDOW_MINUTES: int = Field(default=120, description="Minutes for active evaluation window (default 2h)")
    SIMULATION_RANDOM_SEED: int = Field(default=42, description="Default PRNG seed for deterministic synthetic generation")

    # Phase 6: AI Copilot & Evidence-Grounded Reasoning Configuration
    AI_ENABLED: bool = Field(default=True, description="Enable AI Copilot diagnostic assistance")
    AI_PROVIDER: str = Field(default="mock", description="AI provider backend (mock, openai, anthropic, gemini)")
    AI_MODEL: str = Field(default="gpt-4o-mini", description="AI model identifier")
    AI_API_KEY: str | None = Field(default=None, description="API key for cloud LLM provider")
    AI_TEMPERATURE: float = Field(default=0.2, description="Sampling temperature for grounded reasoning")
    AI_MAX_TOKENS: int = Field(default=1024, description="Max token limit per LLM completion")
    AI_TIMEOUT_SECONDS: float = Field(default=15.0, description="HTTP timeout for AI completion requests")
    AI_DEMO_MODE: bool = Field(default=True, description="Enable deterministic fallback mode when API key is unset")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure postgres URLs use the asyncpg driver."""
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    def get_cors_origins(self) -> list[str]:
        """Parse comma-separated CORS allowed origins into a list of strings."""
        if not self.CORS_ALLOWED_ORIGINS:
            return ["http://localhost:3000"]
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Check if application is running in production."""
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        """Check if application is running in development."""
        return self.APP_ENV == "development"

    @property
    def is_testing(self) -> bool:
        """Check if application is running in test suite."""
        return self.APP_ENV == "testing"


@lru_cache
def get_settings() -> Settings:
    """Cached singleton getter for application settings."""
    return Settings()
