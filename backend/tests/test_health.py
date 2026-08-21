"""Unit and integration tests for liveness and readiness health probe endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness_endpoint_success(client: AsyncClient) -> None:
    """Verify /api/v1/health/live returns HTTP 200 with status ok."""
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok"}
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_readiness_endpoint_healthy_db(client: AsyncClient) -> None:
    """Verify /api/v1/health/ready returns HTTP 200 when database is healthy."""
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_readiness_endpoint_unhealthy_db(failing_db_client: AsyncClient) -> None:
    """Verify /api/v1/health/ready returns HTTP 503 when database query fails."""
    response = await failing_db_client.get("/api/v1/health/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unavailable"
    assert data["database"] == "unavailable"
    # Ensure sensitive database stack traces or credentials are NOT leaked in response
    assert "password" not in str(data).lower()
    assert "connectionrefused" not in str(data).lower()
