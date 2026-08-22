"""Async SQLAlchemy session factory and dependency injection for FastAPI."""

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("app.db")

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get or initialize the global async SQLAlchemy engine with connection pooling."""
    global _engine, _session_factory
    if _engine is None:
        settings = get_settings()
        db_url = settings.DATABASE_URL

        if "postgresql" in db_url and ("localhost" in db_url or "127.0.0.1" in db_url):
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            conn_res = sock.connect_ex(("127.0.0.1", 5432))
            sock.close()
            if conn_res != 0:
                logger.warning(
                    "PostgreSQL port 5432 is not reachable. Falling back to local SQLite database: sqlite+aiosqlite:///./recover_ai.db"
                )
                db_url = "sqlite+aiosqlite:///./recover_ai.db"

        logger.info(
            f"Initializing async database engine ({db_url})"
        )
        engine_kwargs: dict = {
            "echo": settings.DB_ECHO,
        }
        if "sqlite" not in db_url:
            engine_kwargs.update({
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_timeout": settings.DB_POOL_TIMEOUT,
                "pool_recycle": settings.DB_POOL_RECYCLE,
                "pool_pre_ping": True,
            })

        _engine = create_async_engine(db_url, **engine_kwargs)
        _session_factory = async_sessionmaker(
            bind=_engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get the initialized async session factory."""
    if _session_factory is None:
        get_engine()
    assert _session_factory is not None
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a transactional async database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            raise exc


async def close_db_engine() -> None:
    """Gracefully dispose of the database engine and connection pool on shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        logger.info("Disposing async database connection pool...")
        await _engine.dispose()
        _engine = None
        _session_factory = None
