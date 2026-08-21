"""End-to-end integration tests for the Risk Detection Engine with database persistence."""

import uuid
import pytest
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Merchant, RiskCase, RiskSignal, AuditLog
from app.schemas.risk_engine import RiskAnalysisRequest
from app.services.ingestion.ingestor import TransactionIngestionService
from app.services.risk.engine import RiskDetectionEngine
from app.services.simulation.generator import SyntheticTransactionGenerator

TEST_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
async def seeded_merchant(db_session: AsyncSession) -> Merchant:
    """Ensure test merchant exists."""
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
    return merchant


@pytest.mark.asyncio
async def test_upi_degradation_e2e_detection_and_case_creation(
    db_session: AsyncSession, seeded_merchant: Merchant
):
    """Verify that ingesting a UPI degradation stream triggers risk signals and creates a RiskCase in PostgreSQL."""
    ingestor = TransactionIngestionService(db_session)
    risk_engine = RiskDetectionEngine(db_session)

    # 1. Ingest baseline history (300 transactions from 24h to 3h ago)
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    base_start = now - datetime.timedelta(hours=24)
    base_end = now - datetime.timedelta(hours=3)
    gen_base = SyntheticTransactionGenerator(seed=1001, merchant_id=TEST_MERCHANT_ID)
    base_batch = gen_base.generate_batch(count=300, scenario_id="NORMAL_BASELINE", start_time=base_start, end_time=base_end)
    await ingestor.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=base_batch)

    # 2. Ingest degraded stream (300 transactions in active 2h window with UPI degradation)
    deg_start = now - datetime.timedelta(hours=2)
    deg_end = now
    gen_deg = SyntheticTransactionGenerator(seed=1002, merchant_id=TEST_MERCHANT_ID)
    deg_batch = gen_deg.generate_batch(count=300, scenario_id="UPI_DEGRADATION", start_time=deg_start, end_time=deg_end)
    await ingestor.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=deg_batch)

    # 3. Trigger risk analysis
    analysis_req = RiskAnalysisRequest(
        merchant_id=TEST_MERCHANT_ID,
        current_window_minutes=120,
        baseline_window_minutes=1440,
        dry_run=False,
    )
    analysis_res = await risk_engine.analyze(analysis_req)

    # 4. Verify detection results
    assert analysis_res.signals_detected_count >= 1
    assert analysis_res.risk_case_created is True
    assert analysis_res.severity in ["HIGH", "CRITICAL", "MEDIUM"]
    assert analysis_res.revenue_at_risk > 0

    # 5. Verify RiskCase persisted in DB
    cases_stmt = select(RiskCase).where(RiskCase.merchant_id == TEST_MERCHANT_ID)
    cases = (await db_session.execute(cases_stmt)).scalars().all()
    assert len(cases) >= 1
    primary_case = cases[0]
    assert "UPI" in primary_case.title

    # 6. Verify RiskSignals persisted in DB
    signals_stmt = select(RiskSignal).where(RiskSignal.risk_case_id == primary_case.id)
    signals = (await db_session.execute(signals_stmt)).scalars().all()
    assert len(signals) >= 1

    # 7. Verify Audit Log recorded
    audit_stmt = select(AuditLog).where(
        AuditLog.merchant_id == TEST_MERCHANT_ID,
        AuditLog.action == "RISK_DETECTED",
    )
    logs = (await db_session.execute(audit_stmt)).scalars().all()
    assert len(logs) >= 1


@pytest.mark.asyncio
async def test_case_idempotency_prevents_duplicate_cases(
    db_session: AsyncSession, seeded_merchant: Merchant
):
    """Verify that re-running risk analysis on the same incident updates existing case rather than creating duplicates."""
    ingestor = TransactionIngestionService(db_session)
    risk_engine = RiskDetectionEngine(db_session)

    gen = SyntheticTransactionGenerator(seed=2001, merchant_id=TEST_MERCHANT_ID)
    batch = gen.generate_batch(count=200, scenario_id="UPI_DEGRADATION")
    await ingestor.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch)

    # First analysis run
    res1 = await risk_engine.analyze(
        RiskAnalysisRequest(merchant_id=TEST_MERCHANT_ID, current_window_minutes=120, dry_run=False)
    )
    case_count_1 = len((await db_session.execute(select(RiskCase).where(RiskCase.merchant_id == TEST_MERCHANT_ID))).scalars().all())

    # Second analysis run on the same open incident
    res2 = await risk_engine.analyze(
        RiskAnalysisRequest(merchant_id=TEST_MERCHANT_ID, current_window_minutes=120, dry_run=False)
    )
    case_count_2 = len((await db_session.execute(select(RiskCase).where(RiskCase.merchant_id == TEST_MERCHANT_ID))).scalars().all())

    assert case_count_1 == case_count_2
    assert res1.risk_case_id == res2.risk_case_id
