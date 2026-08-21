"""FastAPI router for Transaction Pipeline Orchestration and Operational Telemetry."""

import uuid
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.pipeline import (
    PipelineMetricsResponse,
    PipelineRunRequest,
    PipelineRunResponse,
    PipelineStatusResponse,
)
from app.services.pipeline.pipeline import TransactionPipelineService

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


@router.get(
    "/status",
    response_model=PipelineStatusResponse,
    summary="Get Pipeline Status",
    description="Retrieve live pipeline processing state, accepted vs rejected counts, and active incident tallies.",
)
async def get_pipeline_status(
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    db: AsyncSession = Depends(get_db),
) -> PipelineStatusResponse:
    """Get pipeline status and counts."""
    service = TransactionPipelineService(db)
    return await service.get_status(merchant_id=merchant_id)


@router.get(
    "/metrics",
    response_model=PipelineMetricsResponse,
    summary="Get Pipeline Metrics",
    description="Retrieve throughput statistics, average ingestion and risk evaluation latencies, and database records count.",
)
async def get_pipeline_metrics(
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    db: AsyncSession = Depends(get_db),
) -> PipelineMetricsResponse:
    """Get pipeline throughput and latency benchmarks."""
    service = TransactionPipelineService(db)
    return await service.get_metrics(merchant_id=merchant_id)


@router.post(
    "/run",
    response_model=PipelineRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Full Pipeline Run",
    description="Trigger end-to-end execution: generate synthetic stream -> validate -> ingest -> evaluate risk engine -> record audit trail.",
)
async def execute_pipeline_run(
    request: PipelineRunRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
) -> PipelineRunResponse:
    """Execute end-to-end synthetic pipeline run."""
    service = TransactionPipelineService(db)
    req_id = getattr(req.state, "request_id", None)
    return await service.run_pipeline(request=request, request_id=req_id)
