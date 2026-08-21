"""Unit tests for InvestigationContextBuilder."""

import datetime
import uuid
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Merchant, RiskCase
from app.services.ai.context_builder import InvestigationContextBuilder
from app.services.ingestion.ingestor import TransactionIngestionService
from app.services.simulation.generator import SyntheticTransactionGenerator

TEST_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
async def setup_test_context_data(db_session: AsyncSession) -> RiskCase:
    """Fixture ensuring merchant, payments, and risk case exist in the session."""
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

    gen = SyntheticTransactionGenerator(seed=601, merchant_id=TEST_MERCHANT_ID)
    batch = gen.generate_batch(count=80, scenario_id="UPI_DEGRADATION")
    await ingestor.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch)

    case = RiskCase(
        id=uuid.uuid4(),
        merchant_id=TEST_MERCHANT_ID,
        case_reference="RC-CTX-01",
        risk_type="PAYMENT_DEGRADATION",
        severity="HIGH",
        status="OPEN",
        title="UPI Payment Degradation",
        summary="Automated telemetry detected drop in UPI conversions",
        revenue_at_risk=Decimal("1219544.00"),
        estimated_recoverable_revenue=Decimal("304886.00"),
        confidence_score=Decimal("0.8300"),
        detected_at=now,
    )
    db_session.add(case)
    await db_session.commit()
    return case


@pytest.mark.asyncio
async def test_investigation_context_builder_structures_verified_facts(
    db_session: AsyncSession, setup_test_context_data: RiskCase
):
    """Test that context builder loads investigation and structures factual payload."""
    case = setup_test_context_data
    builder = InvestigationContextBuilder(db_session)

    # Build context for the case
    ctx = await builder.build_context(
        merchant_id=TEST_MERCHANT_ID,
        investigation_ref=case.case_reference,
    )

    assert "case" in ctx
    assert "metrics" in ctx
    assert "impact" in ctx
    assert "root_cause" in ctx
    assert "evidence" in ctx
    assert "evidence_ids" in ctx
    assert "timeline" in ctx
    assert "recommendation" in ctx

    metrics = ctx["metrics"]
    assert metrics["total_transactions"] > 0
    assert metrics["overall_success_rate"] > 0
    assert metrics["primary_affected_bank"] in ("HDFC", "SBI", "ICICI", "AXIS")
    assert metrics["primary_affected_payment_method"] in ("UPI", "CARD", "NETBANKING", "WALLET")


    impact = ctx["impact"]
    assert "1,219,544.00" in impact["revenue_at_risk_inr"]
    assert "304,886.00" in impact["recoverable_revenue_inr"]

    evidence_ids = ctx["evidence_ids"]
    assert len(evidence_ids) >= 4
