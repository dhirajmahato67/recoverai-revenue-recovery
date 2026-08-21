"""Unit tests for the deterministic Root Cause Analysis Engine."""

import datetime
import uuid
import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Merchant, RiskCase
from app.services.ingestion.ingestor import TransactionIngestionService
from app.services.investigation.collectors import (
    BankEvidenceCollector,
    ErrorEvidenceCollector,
    PaymentMethodEvidenceCollector,
    TransactionEvidenceCollector,
)
from app.services.investigation.context import InvestigationContext
from app.services.investigation.root_cause import RootCauseAnalysisEngine
from app.services.simulation.generator import SyntheticTransactionGenerator

TEST_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
async def setup_degradation_context(db_session: AsyncSession) -> InvestigationContext:
    """Fixture providing initialized context with UPI degradation."""
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

    gen_base = SyntheticTransactionGenerator(seed=301, merchant_id=TEST_MERCHANT_ID)
    batch_base = gen_base.generate_batch(
        count=150, scenario_id="NORMAL_BASELINE", start_time=now - datetime.timedelta(hours=12), end_time=now - datetime.timedelta(hours=3)
    )
    await ingestor.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch_base)

    gen_deg = SyntheticTransactionGenerator(seed=302, merchant_id=TEST_MERCHANT_ID)
    batch_deg = gen_deg.generate_batch(
        count=150, scenario_id="UPI_DEGRADATION", start_time=now - datetime.timedelta(hours=2), end_time=now
    )
    await ingestor.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch_deg)

    case = RiskCase(
        id=uuid.uuid4(),
        merchant_id=TEST_MERCHANT_ID,
        case_reference="RC-TEST-02",
        risk_type="PAYMENT_DEGRADATION",
        severity="HIGH",
        status="OPEN",
        title="UPI Payment Degradation",
        summary="Automated telemetry detected drop in UPI conversions",
        revenue_at_risk=Decimal("250000.00"),
        estimated_recoverable_revenue=Decimal("62500.00"),
        confidence_score=Decimal("0.9200"),
        detected_at=now,
    )
    db_session.add(case)
    await db_session.commit()

    ctx = InvestigationContext(db_session, TEST_MERCHANT_ID, case, current_window_minutes=120)
    return await ctx.initialize()


@pytest.mark.asyncio
async def test_root_cause_ranking_and_reasoning(setup_degradation_context: InvestigationContext):
    """Test that RootCauseAnalysisEngine deterministically ranks HDFC UPI degradation #1."""
    ctx = setup_degradation_context
    collectors = [
        TransactionEvidenceCollector(),
        PaymentMethodEvidenceCollector(),
        BankEvidenceCollector(),
        ErrorEvidenceCollector(),
    ]
    all_evidence = []
    for col in collectors:
        all_evidence.extend(col.collect(ctx))

    engine = RootCauseAnalysisEngine()
    (
        primary_root_cause,
        confidence_int,
        finding,
        bullets,
        conclusion,
        candidates,
        tree_nodes,
        evidence_nodes,
    ) = engine.analyze(ctx, all_evidence)

    # 1. Primary root cause check
    assert "HDFC" in primary_root_cause or "UPI" in primary_root_cause
    assert confidence_int >= 80

    # 2. Candidate ranking
    assert len(candidates) >= 3
    assert candidates[0].rank == 1
    assert "HDFC" in candidates[0].cause or "UPI" in candidates[0].cause
    assert candidates[0].score >= candidates[1].score

    # 3. Structured reasoning
    assert len(bullets) >= 3
    assert len(conclusion) > 10

    # 4. Tree structure
    assert len(tree_nodes) >= 1
    assert tree_nodes[0].children is not None
