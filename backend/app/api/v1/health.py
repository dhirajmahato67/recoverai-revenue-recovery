"""Health and readiness probe API endpoints."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.health import check_db_health
from app.schemas.common import HealthResponse, ReadinessResponse, ErrorResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/live",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Liveness Probe",
    description="Determines whether the FastAPI application process is alive and responsive. Does not check downstream database connectivity.",
)
async def liveness_check() -> HealthResponse:
    """Check process liveness."""
    return HealthResponse(status="ok")


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={
        status.HTTP_200_OK: {
            "model": ReadinessResponse,
            "description": "Application is healthy and ready to serve traffic.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ReadinessResponse,
            "description": "Application or required database dependency is unhealthy.",
        },
    },
    summary="Service Readiness Probe",
    description="Determines whether the application is fully operational and capable of serving database-backed traffic by executing a lightweight SELECT 1 query.",
)
async def readiness_check(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> ReadinessResponse:
    """Check application and database readiness."""
    is_db_healthy, _ = await check_db_health(db)

    if not is_db_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status="unavailable",
            database="unavailable",
        )

    return ReadinessResponse(
        status="ok",
        database="ok",
    )
