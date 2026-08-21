"""End-to-end integration test for the full investigation intelligence workflow."""

import datetime
import uuid
import pytest
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AgentRun, AgentToolCall, AuditLog, Investigation, Merchant, RiskCase, RiskSignal
from app.schemas.risk_engine import RiskAnalysisRequest
from app.services.ingestion.ingestor import TransactionIngestionService
from app.services.investigation.orchestrator import InvestigationOrchestrator
from app.services.risk.engine import RiskDetectionEngine
from app.services.simulation.generator import SyntheticTransactionGenerator

TEST_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.mark.asyncio
async def test_full_incident_to_investigation_e2e_flow(db_session: AsyncSession):
    """Verify full end-to-end: payment ingestion -> risk detection -> case creation -> investigation -> root cause -> persistence."""
    # 1. Ensure merchant
    merchant = await db_session.get(Merchant, TEST_MERCHANT_ID)
    if not merchant:
        merchant = Merchant(
            id=TEST_MERCHANT_ID,
            name="Acme Commerce",
            legal_name="Acme Digital Retail Technologies Pvt Ltd",
            currency="INR",
            timezone="Asia/Kolkata",
            status="ACTIVE",
            external_reference="acme_commerce",
        )
        db_session.add(merchant)
        await db_session.commit()

    ingestor = TransactionIngestionService(db_session)
    risk_engine = RiskDetectionEngine(db_session)
    orchestrator = InvestigationOrchestrator(db_session)

    now = datetime.datetime.now(datetime.timezone.utc)

    # 2. Ingest baseline transactions
    gen_base = SyntheticTransactionGenerator(seed=601, merchant_id=TEST_MERCHANT_ID)
    batch_base = gen_base.generate_batch(
        count=200, scenario_id="NORMAL_BASELINE", start_time=now - datetime.timedelta(hours=24), end_time=now - datetime.timedelta(hours=3)
    )
    await ingestor.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch_base)

    # 3. Ingest degraded transactions
    gen_deg = SyntheticTransactionGenerator(seed=602, merchant_id=TEST_MERCHANT_ID)
    batch_deg = gen_deg.generate_batch(
        count=200, scenario_id="UPI_DEGRADATION", start_time=now - datetime.timedelta(hours=2), end_time=now
    )
    await ingestor.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch_deg)

    # 4. Trigger Risk Detection Engine
    risk_res = await risk_engine.analyze(
        RiskAnalysisRequest(
            merchant_id=TEST_MERCHANT_ID,
            current_window_minutes=120,
            baseline_window_minutes=1440,
            dry_run=False,
        )
    )
    assert risk_res.signals_detected_count >= 1
    case_ref = risk_res.case_reference or "RC-001"

    # 5. Run Investigation Orchestrator
    inv_res = await orchestrator.run_investigation(
        merchant_id=TEST_MERCHANT_ID,
        risk_case_id=case_ref,
        force_reanalyze=False,
    )

    # 6. Verify Investigation findings
    assert inv_res.status == "COMPLETED"
    assert inv_res.confidenceScore >= 80
    assert "HDFC" in inv_res.conclusion or "UPI" in inv_res.conclusion
    assert len(inv_res.steps) >= 5
    assert len(inv_res.toolExecutions) >= 4
    assert len(inv_res.timeline) >= 4
    assert inv_res.recommendedRecovery.eligible_transactions > 0

    # 7. Verify Database Persistence in PostgreSQL
    inv_db = (
        await db_session.execute(
            select(Investigation).where(Investigation.risk_case_id == uuid.UUID(str(risk_res.risk_case_id)))
        )
    ).scalar_one_or_none()
    assert inv_db is not None
    assert inv_db.status == "COMPLETED"
    assert inv_db.confidence_score >= Decimal("0.8000")

    runs = (
        await db_session.execute(
            select(AgentRun).where(AgentRun.risk_case_id == uuid.UUID(str(risk_res.risk_case_id)))
        )
    ).scalars().all()
    assert len(runs) >= 1

    tcs = (
        await db_session.execute(
            select(AgentToolCall).where(AgentToolCall.agent_run_id == runs[0].id)
        )
    ).scalars().all()
    assert len(tcs) >= 4

    audit_logs = (
        await db_session.execute(
            select(AuditLog).where(
                AuditLog.merchant_id == TEST_MERCHANT_ID,
                AuditLog.resource_type == "Investigation",
            )
        )
    ).scalars().all()
    assert len(audit_logs) >= 2
