"""Pydantic schemas for the Pipeline status, telemetry, and execution orchestrator."""

import datetime
import uuid
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.simulation import ScenarioType


class PipelineStatusResponse(BaseModel):
    """Pipeline health, state, and cumulative operational metrics."""

    status: Literal["healthy", "degraded", "recovering", "idle", "running"]
    last_run: datetime.datetime | None = None
    transactions_processed: int
    accepted: int
    duplicates: int
    rejected: int
    risk_signals: int
    risk_cases: int
    processing_duration_ms: float
    environment: str = "development"
    model_config = ConfigDict(extra="ignore")


class PipelineMetricsResponse(BaseModel):
    """Pipeline throughput, latency, and ingestion rates."""

    throughput_tx_per_sec: float
    avg_ingestion_latency_ms: float
    avg_risk_analysis_latency_ms: float
    total_pipeline_runs: int
    last_scenario_executed: str | None = None
    total_database_records: dict[str, int] = Field(default_factory=dict)
    model_config = ConfigDict(extra="ignore")


class PipelineRunRequest(BaseModel):
    """Request to trigger full end-to-end pipeline run (generate -> ingest -> risk analyze)."""

    merchant_id: uuid.UUID
    scenario: ScenarioType = "UPI_DEGRADATION"
    count: int = Field(default=500, ge=10, le=50000)
    seed: int | None = None
    trigger_risk_analysis: bool = True
    model_config = ConfigDict(extra="ignore")


class PipelineRunResponse(BaseModel):
    """Execution results from full end-to-end pipeline execution."""

    merchant_id: uuid.UUID
    pipeline_id: str
    scenario: ScenarioType
    seed: int
    total_generated: int
    ingestion: dict[str, Any]
    risk_analysis: dict[str, Any] | None = None
    total_duration_ms: float
    model_config = ConfigDict(extra="ignore")
