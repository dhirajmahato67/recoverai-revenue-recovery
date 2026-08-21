"""FastAPI router for Synthetic Transaction Simulation endpoints."""

import time
import uuid
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.simulation import (
    GenerateTransactionsRequest,
    GenerateTransactionsResponse,
    ScenarioConfig,
    ScenarioInfo,
    ScenarioType,
)
from app.services.ingestion.ingestor import TransactionIngestionService
from app.services.simulation.generator import SyntheticTransactionGenerator
from app.services.simulation.scenarios import ScenarioRegistry

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.get(
    "/scenarios",
    response_model=list[ScenarioInfo],
    summary="List Simulation Scenarios",
    description="Retrieve catalog of supported synthetic payment scenarios (e.g. UPI Degradation, Normal Baseline).",
)
async def list_scenarios() -> list[ScenarioInfo]:
    """List all available scenario metadata definitions."""
    return ScenarioRegistry.list_scenarios()


@router.post(
    "/scenarios",
    response_model=ScenarioConfig,
    summary="Get Scenario Details",
    description="Get specific scenario operational rules and target conversion thresholds.",
)
async def get_scenario(scenario_id: ScenarioType = Query("NORMAL_BASELINE")) -> ScenarioConfig:
    """Retrieve detailed scenario configuration."""
    return ScenarioRegistry.get_scenario(scenario_id)


@router.post(
    "/generate",
    response_model=GenerateTransactionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Synthetic Transactions",
    description="Generate a batch of synthetic payment transactions with deterministic seeding. Optionally persist directly to PostgreSQL.",
)
async def generate_transactions(
    request: GenerateTransactionsRequest,
    db: AsyncSession = Depends(get_db),
) -> GenerateTransactionsResponse:
    """Generate synthetic transactions stream."""
    seed = request.seed if request.seed is not None else int(time.time()) % 100000
    generator = SyntheticTransactionGenerator(seed=seed, merchant_id=request.merchant_id)

    batch = generator.generate_batch(
        count=request.count,
        scenario_id=request.scenario,
        start_time=request.start_time,
        end_time=request.end_time,
    )

    success_items = [tx for tx in batch if tx.status == "CAPTURED"]
    failed_items = [tx for tx in batch if tx.status == "FAILED"]

    total_vol = sum((tx.amount for tx in batch), Decimal("0.00"))
    failed_vol = sum((tx.amount for tx in failed_items), Decimal("0.00"))
    success_rate = len(success_items) / len(batch) if batch else 0.0

    ingestion_summary = None
    if request.persist:
        ingestion_service = TransactionIngestionService(db)
        ingest_res = await ingestion_service.ingest_batch(
            merchant_id=request.merchant_id,
            transactions=batch,
        )
        ingestion_summary = ingest_res.model_dump()

    # Limit preview sample to 25 items
    sample = batch[:25]

    return GenerateTransactionsResponse(
        merchant_id=request.merchant_id,
        scenario=request.scenario,
        seed=seed,
        count=len(batch),
        success_count=len(success_items),
        failed_count=len(failed_items),
        overall_success_rate=round(success_rate, 4),
        total_volume_inr=total_vol,
        failed_volume_inr=failed_vol,
        persisted=request.persist,
        ingestion_summary=ingestion_summary,
        sample_transactions=sample,
    )


@router.post(
    "/generate/batch",
    response_model=GenerateTransactionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch Generate Synthetic Stream",
    description="Alias for generate transactions endpoint.",
)
async def generate_batch_transactions(
    request: GenerateTransactionsRequest,
    db: AsyncSession = Depends(get_db),
) -> GenerateTransactionsResponse:
    """Batch generate alias."""
    return await generate_transactions(request=request, db=db)
