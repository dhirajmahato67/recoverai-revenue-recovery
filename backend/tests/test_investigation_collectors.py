"""Unit tests for modular evidence collectors."""

import datetime
import uuid
import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Merchant, RiskCase
from app.services.ingestion.ingestor import TransactionIngestionService
from app.services.investigation.collectors import (
    AuditEvidenceCollector,
    BankEvidenceCollector,
    ErrorEvidenceCollector,
    PaymentMethodEvidenceCollector,
    RiskSignalEvidenceCollector,
    TemporalEvidenceCollector,
    TransactionEvidenceCollector,
)
from app.services.investigation.context import InvestigationContext
from app.services.simulation.generator import SyntheticTransactionGenerator

TEST_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
async def setup_investigation_context(db_session: AsyncSession) -> InvestigationContext:
    """Fixture providing initialized investigation context with real data."""
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

    # Ingest baseline and degraded transactions
    ingestor = TransactionIngestionService(db_session)
    now = datetime.datetime.now(datetime.timezone.utc)

    gen_base = SyntheticTransactionGenerator(seed=100, merchant_id=TEST_MERCHANT_ID)
    batch_base = gen_base.generate_batch(
        count=150, scenario_id="NORMAL_BASELINE", start_time=now - datetime.timedelta(hours=12), end_time=now - datetime.timedelta(hours=3)
    )
    await ingestor.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch_base)

    gen_deg = SyntheticTransactionGenerator(seed=200, merchant_id=TEST_MERCHANT_ID)
    batch_deg = gen_deg.generate_batch(
        count=150, scenario_id="UPI_DEGRADATION", start_time=now - datetime.timedelta(hours=2), end_time=now
    )
    await ingestor.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch_deg)

    # Risk case
    case = RiskCase(
        id=uuid.uuid4(),
        merchant_id=TEST_MERCHANT_ID,
        case_reference="RC-TEST-01",
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
async def test_transaction_evidence_collector(setup_investigation_context: InvestigationContext):
    """Test volume and overall conversion evidence."""
    collector = TransactionEvidenceCollector()
    evidence = collector.collect(setup_investigation_context)
    assert len(evidence) >= 2
    types = [e.type for e in evidence]
    assert "TRANSACTION_VOLUME" in types
    assert "PAYMENT_SUCCESS_RATE" in types


@pytest.mark.asyncio
async def test_payment_method_evidence_collector(setup_investigation_context: InvestigationContext):
    """Test payment method degradation evidence."""
    collector = PaymentMethodEvidenceCollector()
    evidence = collector.collect(setup_investigation_context)
    assert len(evidence) >= 1
    upi_ev = next((e for e in evidence if "upi" in e.metric.lower()), None)
    assert upi_ev is not None
    assert upi_ev.delta < 0  # Negative delta for UPI


@pytest.mark.asyncio
async def test_bank_evidence_collector(setup_investigation_context: InvestigationContext):
    """Test issuer bank degradation evidence."""
    collector = BankEvidenceCollector()
    evidence = collector.collect(setup_investigation_context)
    assert len(evidence) >= 1
    hdfc_ev = next((e for e in evidence if "hdfc" in e.metric.lower()), None)
    assert hdfc_ev is not None


@pytest.mark.asyncio
async def test_error_evidence_collector(setup_investigation_context: InvestigationContext):
    """Test error code frequency evidence."""
    collector = ErrorEvidenceCollector()
    evidence = collector.collect(setup_investigation_context)
    assert len(evidence) >= 1
    codes = [e.details.get("error_code") for e in evidence]
    assert any(c in ["GATEWAY_TIMEOUT", "BANK_DECLINED"] for c in codes)


@pytest.mark.asyncio
async def test_temporal_evidence_collector(setup_investigation_context: InvestigationContext):
    """Test temporal bucket distribution evidence."""
    collector = TemporalEvidenceCollector()
    evidence = collector.collect(setup_investigation_context)
    assert len(evidence) >= 1
    assert evidence[0].type == "TEMPORAL_DISTRIBUTION"
