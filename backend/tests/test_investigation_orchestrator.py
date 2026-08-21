"""Unit tests for the Investigation Orchestration service."""

import datetime
import uuid
import pytest
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AgentRun, AgentToolCall, AuditLog, Investigation, Merchant, RiskCase
from app.services.ingestion.ingestor import TransactionIngestionService
from app.services.investigation.orchestrator import InvestigationOrchestrator
from app.services.simulation.generator import SyntheticTransactionGenerator

TEST_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
async def setup_merchant_and_case(db_session: AsyncSession) -> RiskCase:
    """Fixture providing merchant and active risk case."""
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
    now = datetime.datetime.now(datetime.timezone.utc)

    gen = SyntheticTransactionGenerator(seed=401, merchant_id=TEST_MERCHANT_ID)
    batch = gen.generate_batch(count=100, scenario_id="UPI_DEGRADATION")
    await ingestor.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch)

    case = RiskCase(
        id=uuid.uuid4(),
        merchant_id=TEST_MERCHANT_ID,
        case_reference="RC-ORCH-01",
        risk_type="PAYMENT_DEGRADATION",
        severity="HIGH",
        status="OPEN",
        title="UPI Payment Degradation",
        summary="Automated telemetry detected drop in UPI conversions",
        revenue_at_risk=Decimal("180000.00"),
        estimated_recoverable_revenue=Decimal("45000.00"),
        confidence_score=Decimal("0.9100"),
        detected_at=now,
    )
    db_session.add(case)
    await db_session.commit()
    return case


@pytest.mark.asyncio
async def test_investigation_orchestration_lifecycle_and_idempotency(
    db_session: AsyncSession, setup_merchant_and_case: RiskCase
):
    """Verify that orchestrator runs full diagnostic workflow, logs tool calls, and is idempotent."""
    case = setup_merchant_and_case
    orchestrator = InvestigationOrchestrator(db_session)

    # 1. First execution
    res1 = await orchestrator.run_investigation(
        merchant_id=TEST_MERCHANT_ID,
        risk_case_id=case.case_reference,
        force_reanalyze=False,
    )
    assert res1.status == "COMPLETED"
    assert res1.confidenceScore >= 80
    assert len(res1.steps) >= 5
    assert len(res1.toolExecutions) >= 4

    # 2. Verify persisted entities in PostgreSQL
    inv_stmt = select(Investigation).where(Investigation.risk_case_id == case.id)
    invs = (await db_session.execute(inv_stmt)).scalars().all()
    assert len(invs) == 1
    assert invs[0].status == "COMPLETED"

    runs_stmt = select(AgentRun).where(AgentRun.risk_case_id == case.id)
    runs = (await db_session.execute(runs_stmt)).scalars().all()
    assert len(runs) >= 1

    tc_stmt = select(AgentToolCall).where(AgentToolCall.agent_run_id == runs[0].id)
    tcs = (await db_session.execute(tc_stmt)).scalars().all()
    assert len(tcs) >= 4

    audit_stmt = select(AuditLog).where(
        AuditLog.merchant_id == TEST_MERCHANT_ID,
        AuditLog.resource_type == "Investigation",
    )
    audits = (await db_session.execute(audit_stmt)).scalars().all()
    assert len(audits) >= 2

    # 3. Second execution (Idempotent check - must not create duplicate investigations)
    res2 = await orchestrator.run_investigation(
        merchant_id=TEST_MERCHANT_ID,
        risk_case_id=case.case_reference,
        force_reanalyze=False,
    )
    invs_after = (await db_session.execute(inv_stmt)).scalars().all()
    assert len(invs_after) == 1
    assert res1.id == res2.id
