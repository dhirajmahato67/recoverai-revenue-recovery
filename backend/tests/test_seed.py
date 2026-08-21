"""Tests verifying seed script determinism, completeness, and idempotency."""

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Merchant,
    User,
    Customer,
    Order,
    Payment,
    PaymentEvent,
    RiskCase,
    Investigation,
    RecoveryPlan,
    RecoveryBatch,
)
from app.db.seed import seed_database, ACME_MERCHANT_ID


@pytest.mark.asyncio
async def test_seed_database_execution_and_idempotency(db_session: AsyncSession) -> None:
    """Verify seed script populates data correctly and running twice creates zero duplicate records."""
    # 1. First execution
    await seed_database(db_session)

    # Verify Acme Merchant exists
    merchant = await db_session.get(Merchant, ACME_MERCHANT_ID)
    assert merchant is not None
    assert merchant.name == "Acme Commerce"
    assert merchant.currency == "INR"

    # Count records
    user_count_1 = (await db_session.execute(select(func.count()).select_from(User))).scalar()
    cust_count_1 = (await db_session.execute(select(func.count()).select_from(Customer))).scalar()
    order_count_1 = (await db_session.execute(select(func.count()).select_from(Order))).scalar()
    payment_count_1 = (await db_session.execute(select(func.count()).select_from(Payment))).scalar()
    case_count_1 = (await db_session.execute(select(func.count()).select_from(RiskCase))).scalar()
    batch_count_1 = (await db_session.execute(select(func.count()).select_from(RecoveryBatch))).scalar()

    assert user_count_1 == 3
    assert cust_count_1 == 25
    assert order_count_1 == 350
    assert payment_count_1 == 350
    assert case_count_1 == 1
    assert batch_count_1 == 1

    # 2. Second execution (must be 100% idempotent)
    await seed_database(db_session)

    user_count_2 = (await db_session.execute(select(func.count()).select_from(User))).scalar()
    cust_count_2 = (await db_session.execute(select(func.count()).select_from(Customer))).scalar()
    order_count_2 = (await db_session.execute(select(func.count()).select_from(Order))).scalar()
    payment_count_2 = (await db_session.execute(select(func.count()).select_from(Payment))).scalar()
    case_count_2 = (await db_session.execute(select(func.count()).select_from(RiskCase))).scalar()
    batch_count_2 = (await db_session.execute(select(func.count()).select_from(RecoveryBatch))).scalar()

    assert user_count_2 == user_count_1
    assert cust_count_2 == cust_count_1
    assert order_count_2 == order_count_1
    assert payment_count_2 == payment_count_1
    assert case_count_2 == case_count_1
    assert batch_count_2 == batch_count_1

    # 3. Verify Payment Method Distribution totals exactly 100%
    all_payments = (await db_session.execute(select(Payment).where(Payment.merchant_id == ACME_MERCHANT_ID))).scalars().all()
    total_payments = len(all_payments)
    assert total_payments == 350

    upi_count = sum(1 for p in all_payments if p.payment_method == "UPI")
    card_count = sum(1 for p in all_payments if p.payment_method == "CARD")
    nb_count = sum(1 for p in all_payments if p.payment_method == "NETBANKING")
    wallet_count = sum(1 for p in all_payments if p.payment_method == "WALLET")

    # Sum of counts must equal total
    assert upi_count + card_count + nb_count + wallet_count == total_payments

    # Check that proportions match intended target (60% UPI, 20% Card, 12% Netbanking, 8% Wallet) within random sampling margin
    assert 0.50 <= (upi_count / total_payments) <= 0.70
    assert 0.14 <= (card_count / total_payments) <= 0.26
    assert 0.08 <= (nb_count / total_payments) <= 0.18
    assert 0.04 <= (wallet_count / total_payments) <= 0.14
