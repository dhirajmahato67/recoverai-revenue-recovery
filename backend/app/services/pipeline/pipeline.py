"""Pipeline orchestrator coordinating synthetic stream generation, ingestion, and risk analysis."""

import datetime
import time
import uuid
from typing import Any
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger
from app.db.models import AuditLog, Customer, Order, Payment, RiskCase, RiskSignal
from app.schemas.pipeline import (
    PipelineMetricsResponse,
    PipelineRunRequest,
    PipelineRunResponse,
    PipelineStatusResponse,
)
from app.schemas.risk_engine import RiskAnalysisRequest
from app.services.ingestion.ingestor import TransactionIngestionService
from app.services.risk.engine import RiskDetectionEngine
from app.services.simulation.generator import SyntheticTransactionGenerator

logger = get_logger("app.services.pipeline")


class PipelineStateTracker:
    """Singleton tracker for pipeline execution telemetry across sessions."""

    def __init__(self) -> None:
        self.total_runs: int = 0
        self.total_processed: int = 0
        self.total_accepted: int = 0
        self.total_duplicates: int = 0
        self.total_rejected: int = 0
        self.total_signals: int = 0
        self.total_cases: int = 0
        self.last_run_time: datetime.datetime | None = None
        self.last_duration_ms: float = 0.0
        self.last_scenario: str | None = None
        self.ingestion_latencies_ms: list[float] = []
        self.risk_latencies_ms: list[float] = []

    def record_run(
        self,
        requested: int,
        accepted: int,
        duplicates: int,
        rejected: int,
        signals: int,
        cases: int,
        ingest_duration_ms: float,
        risk_duration_ms: float,
        total_duration_ms: float,
        scenario: str,
    ) -> None:
        self.total_runs += 1
        self.total_processed += requested
        self.total_accepted += accepted
        self.total_duplicates += duplicates
        self.total_rejected += rejected
        self.total_signals += signals
        self.total_cases += cases
        self.last_run_time = datetime.datetime.now(datetime.timezone.utc)
        self.last_duration_ms = total_duration_ms
        self.last_scenario = scenario
        self.ingestion_latencies_ms.append(ingest_duration_ms)
        self.risk_latencies_ms.append(risk_duration_ms)
        if len(self.ingestion_latencies_ms) > 100:
            self.ingestion_latencies_ms.pop(0)
        if len(self.risk_latencies_ms) > 100:
            self.risk_latencies_ms.pop(0)


# Module-level singleton
pipeline_tracker = PipelineStateTracker()


class TransactionPipelineService:
    """Orchestrates end-to-end synthetic streaming, validation, batch ingestion, and risk analysis."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.ingestion_service = TransactionIngestionService(session)
        self.risk_engine = RiskDetectionEngine(session)

    async def run_pipeline(
        self,
        request: PipelineRunRequest,
        request_id: str | None = None,
    ) -> PipelineRunResponse:
        """Execute full synthetic transaction pipeline run."""
        start_time = time.perf_counter()
        pipeline_id = f"pipe_{uuid.uuid4().hex[:12]}"
        seed = request.seed if request.seed is not None else int(time.time()) % 100000

        logger.info(
            f"Starting pipeline run {pipeline_id} for merchant {request.merchant_id} "
            f"[scenario={request.scenario}, count={request.count}, seed={seed}]"
        )

        # 1. Generate synthetic stream
        generator = SyntheticTransactionGenerator(seed=seed, merchant_id=request.merchant_id)
        batch = generator.generate_batch(count=request.count, scenario_id=request.scenario)

        # 2. Ingest stream into database
        ingest_start = time.perf_counter()
        ingest_res = await self.ingestion_service.ingest_batch(
            merchant_id=request.merchant_id,
            transactions=batch,
            request_id=request_id,
        )
        ingest_duration_ms = (time.perf_counter() - ingest_start) * 1000

        # 3. Analyze risk telemetry
        risk_res_dict: dict[str, Any] | None = None
        signals_count = 0
        cases_count = 0
        risk_duration_ms = 0.0

        if request.trigger_risk_analysis:
            risk_start = time.perf_counter()
            risk_res = await self.risk_engine.analyze(
                RiskAnalysisRequest(
                    merchant_id=request.merchant_id,
                    current_window_minutes=120,
                    baseline_window_minutes=1440,
                    dry_run=False,
                ),
                request_id=request_id,
            )
            risk_duration_ms = (time.perf_counter() - risk_start) * 1000
            signals_count = risk_res.signals_detected_count
            cases_count = 1 if risk_res.risk_case_created else 0
            risk_res_dict = risk_res.model_dump()

        total_duration_ms = (time.perf_counter() - start_time) * 1000

        # 4. Update operational telemetry tracker
        pipeline_tracker.record_run(
            requested=ingest_res.requested,
            accepted=ingest_res.accepted,
            duplicates=ingest_res.duplicates,
            rejected=ingest_res.rejected,
            signals=signals_count,
            cases=cases_count,
            ingest_duration_ms=ingest_duration_ms,
            risk_duration_ms=risk_duration_ms,
            total_duration_ms=total_duration_ms,
            scenario=request.scenario,
        )

        # 5. Record pipeline audit trail
        audit_log = AuditLog(
            merchant_id=request.merchant_id,
            actor_type="SYSTEM",
            actor_id="transaction_pipeline_v1",
            action="PIPELINE_RUN_COMPLETED",
            resource_type="Pipeline",
            resource_id=pipeline_id,
            request_id=request_id,
            metadata_={
                "scenario": request.scenario,
                "seed": seed,
                "requested": ingest_res.requested,
                "accepted": ingest_res.accepted,
                "signals_detected": signals_count,
                "duration_ms": total_duration_ms,
            },
        )
        self.session.add(audit_log)
        await self.session.commit()

        logger.info(f"Pipeline run {pipeline_id} completed successfully in {total_duration_ms:.2f}ms")

        return PipelineRunResponse(
            merchant_id=request.merchant_id,
            pipeline_id=pipeline_id,
            scenario=request.scenario,
            seed=seed,
            total_generated=len(batch),
            ingestion=ingest_res.model_dump(),
            risk_analysis=risk_res_dict,
            total_duration_ms=round(total_duration_ms, 2),
        )

    async def get_status(self, merchant_id: uuid.UUID) -> PipelineStatusResponse:
        """Query real-time database state and operational metrics for pipeline status."""
        total_payments = (
            await self.session.execute(
                select(func.count(Payment.id)).where(Payment.merchant_id == merchant_id)
            )
        ).scalar() or 0

        total_signals = (
            await self.session.execute(
                select(func.count(RiskSignal.id))
                .join(RiskCase, RiskSignal.risk_case_id == RiskCase.id)
                .where(RiskCase.merchant_id == merchant_id)
            )
        ).scalar() or 0

        total_cases = (
            await self.session.execute(
                select(func.count(RiskCase.id)).where(RiskCase.merchant_id == merchant_id)
            )
        ).scalar() or 0

        status = "healthy"
        if pipeline_tracker.last_scenario == "UPI_DEGRADATION" and total_signals > 0:
            status = "degraded"

        return PipelineStatusResponse(
            status=status,  # type: ignore
            last_run=pipeline_tracker.last_run_time,
            transactions_processed=pipeline_tracker.total_processed or total_payments,
            accepted=pipeline_tracker.total_accepted or total_payments,
            duplicates=pipeline_tracker.total_duplicates,
            rejected=pipeline_tracker.total_rejected,
            risk_signals=pipeline_tracker.total_signals or total_signals,
            risk_cases=pipeline_tracker.total_cases or total_cases,
            processing_duration_ms=round(pipeline_tracker.last_duration_ms, 2),
            environment="development",
        )

    async def get_metrics(self, merchant_id: uuid.UUID) -> PipelineMetricsResponse:
        """Query performance benchmarks and aggregate database record tallies."""
        avg_ingest = (
            sum(pipeline_tracker.ingestion_latencies_ms) / len(pipeline_tracker.ingestion_latencies_ms)
            if pipeline_tracker.ingestion_latencies_ms
            else 0.0
        )
        avg_risk = (
            sum(pipeline_tracker.risk_latencies_ms) / len(pipeline_tracker.risk_latencies_ms)
            if pipeline_tracker.risk_latencies_ms
            else 0.0
        )

        throughput = (
            (pipeline_tracker.total_accepted / max(1.0, (pipeline_tracker.last_duration_ms / 1000.0)))
            if pipeline_tracker.last_duration_ms > 0
            else 0.0
        )

        db_counts = {
            "payments": (await self.session.execute(select(func.count(Payment.id)).where(Payment.merchant_id == merchant_id))).scalar() or 0,
            "orders": (await self.session.execute(select(func.count(Order.id)).where(Order.merchant_id == merchant_id))).scalar() or 0,
            "customers": (await self.session.execute(select(func.count(Customer.id)).where(Customer.merchant_id == merchant_id))).scalar() or 0,
            "risk_cases": (await self.session.execute(select(func.count(RiskCase.id)).where(RiskCase.merchant_id == merchant_id))).scalar() or 0,
            "risk_signals": (await self.session.execute(select(func.count(RiskSignal.id)).join(RiskCase, RiskSignal.risk_case_id == RiskCase.id).where(RiskCase.merchant_id == merchant_id))).scalar() or 0,
            "audit_logs": (await self.session.execute(select(func.count(AuditLog.id)).where(AuditLog.merchant_id == merchant_id))).scalar() or 0,
        }

        return PipelineMetricsResponse(
            throughput_tx_per_sec=round(throughput, 2),
            avg_ingestion_latency_ms=round(avg_ingest, 2),
            avg_risk_analysis_latency_ms=round(avg_risk, 2),
            total_pipeline_runs=pipeline_tracker.total_runs,
            last_scenario_executed=pipeline_tracker.last_scenario,
            total_database_records=db_counts,
        )
