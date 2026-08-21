"""Lightweight database connectivity and health probe utility."""

import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger

logger = get_logger("app.db.health")


async def check_db_health(session: AsyncSession, timeout_seconds: float = 3.0) -> tuple[bool, str | None]:
    """Execute a lightweight SELECT 1 query to verify database readiness.

    Returns:
        tuple[bool, str | None]: (is_healthy, error_summary)
    """
    try:
        # Enforce execution timeout to prevent hanging on unresponsive networks
        async with asyncio.timeout(timeout_seconds):
            result = await session.execute(text("SELECT 1"))
            scalar_val = result.scalar()
            if scalar_val == 1:
                return True, None
            return False, "Unexpected database response"
    except asyncio.TimeoutError:
        logger.error("Database health check timed out after %.1fs", timeout_seconds)
        return False, "Database query timed out"
    except Exception as exc:
        # Log the raw exception internally for debugging, but never return it to client
        logger.error("Database health check failed: %s (%s)", exc.__class__.__name__, str(exc))
        return False, "Database connection unavailable"
