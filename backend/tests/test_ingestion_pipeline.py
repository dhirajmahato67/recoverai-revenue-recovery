"""Integration tests for transaction ingestion service and idempotency."""

import uuid
import pytest
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Merchant, Order, Payment, PaymentEvent, AuditLog
from app.schemas.transaction_ingest import TransactionIngestItem
from app.services.ingestion.ingestor import TransactionIngestionService
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
async def test_single_and_batch_ingestion(db_session: AsyncSession, seeded_merchant: Merchant):
    """Test standard batch ingestion creates payments, orders, customers, and events."""
    service = TransactionIngestionService(db_session)
    gen = SyntheticTransactionGenerator(seed=101, merchant_id=TEST_MERCHANT_ID)
    batch = gen.generate_batch(count=20, scenario_id="NORMAL_BASELINE")

    response = await service.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch)

    assert response.requested == 20
    assert response.accepted == 20
    assert response.duplicates == 0
    assert response.rejected == 0

    # Verify payments were persisted
    stmt = select(Payment).where(Payment.merchant_id == TEST_MERCHANT_ID)
    payments = (await db_session.execute(stmt)).scalars().all()
    assert len(payments) == 20

    # Verify audit log was recorded
    audit_stmt = select(AuditLog).where(
        AuditLog.merchant_id == TEST_MERCHANT_ID,
        AuditLog.action == "TRANSACTION_BATCH_INGESTED",
    )
    logs = (await db_session.execute(audit_stmt)).scalars().all()
    assert len(logs) >= 1


@pytest.mark.asyncio
async def test_idempotent_ingestion_duplicate_suppression(db_session: AsyncSession, seeded_merchant: Merchant):
    """Test resubmitting the same batch does not create duplicate payment records."""
    service = TransactionIngestionService(db_session)
    gen = SyntheticTransactionGenerator(seed=202, merchant_id=TEST_MERCHANT_ID)
    batch = gen.generate_batch(count=15, scenario_id="NORMAL_BASELINE")

    # First submission
    resp1 = await service.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch)
    assert resp1.accepted == 15
    assert resp1.duplicates == 0

    # Second identical submission
    resp2 = await service.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch)
    assert resp2.accepted == 0
    assert resp2.duplicates == 15

    # Total in DB should still be exactly 15
    stmt = select(Payment).where(
        Payment.merchant_id == TEST_MERCHANT_ID,
        Payment.external_payment_id.startswith("pay_synth_202_"),
    )
    payments = (await db_session.execute(stmt)).scalars().all()
    assert len(payments) == 15
