"""Pytest configuration, async test client, and in-memory SQLite database fixtures."""

import os
from collections.abc import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

# Set testing environment variables
os.environ["APP_ENV"] = "testing"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.core.config import Settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_application


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Provide testing settings instance."""
    return Settings(
        APP_NAME="RecoverAI Test API",
        APP_ENV="testing",
        DEBUG=True,
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        CORS_ALLOWED_ORIGINS="http://localhost:3000,http://testserver",
        LOG_LEVEL="WARNING",
    )


@pytest.fixture(scope="session")
def test_engine() -> AsyncEngine:
    """Create in-memory async SQLite engine for test session."""
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )


@pytest.fixture(autouse=True)
async def prepare_database(test_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Create all schema tables before tests and drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a fresh transactional AsyncSession for test functions."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client with in-memory database session override."""
    app = create_application()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest.fixture
async def failing_db_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client with simulated failing database session."""
    from unittest.mock import AsyncMock

    mock_failing_session = AsyncMock(spec=AsyncSession)
    mock_failing_session.execute.side_effect = ConnectionRefusedError("Simulated database failure")

    app = create_application()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_failing_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client

    app.dependency_overrides.clear()
