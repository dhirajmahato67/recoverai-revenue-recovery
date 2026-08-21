"""Tests for domain models, constraints, relationships, and Decimal financial precision."""

import datetime
import uuid
from decimal import Decimal
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Merchant,
    User,
    Customer,
    Order,
    Payment,
    PaymentEvent,
    RiskCase,
    RiskSignal,
    Investigation,
    RecoveryPlan,
    RecoveryBatch,
    RecoveryAttempt,
    Approval,
    AuditLog,
    AgentRun,
    AgentToolCall,
)


@pytest.mark.asyncio
async def test_merchant_and_user_creation(db_session: AsyncSession) -> None:
    """Verify merchant and associated user creation and relationship."""
    merchant = Merchant(
        name="Test Merchant Ltd",
        currency="INR",
        timezone="Asia/Kolkata",
        status="ACTIVE",
    )
    db_session.add(merchant)
    await db_session.flush()

    user = User(
        merchant_id=merchant.id,
        email="admin@testmerchant.local",
        full_name="Rajesh Kumar",
        role="ADMIN",
        status="ACTIVE",
    )
    db_session.add(user)
    await db_session.flush()

    assert user.id is not None
    assert user.merchant_id == merchant.id

    from sqlalchemy.orm import selectinload
    stmt = select(Merchant).where(Merchant.id == merchant.id).options(selectinload(Merchant.users))
    result = await db_session.execute(stmt)
    loaded_merchant = result.scalar_one()
    assert len(loaded_merchant.users) == 1
    assert loaded_merchant.users[0].email == "admin@testmerchant.local"


@pytest.mark.asyncio
async def test_unique_user_email_per_merchant(db_session: AsyncSession) -> None:
    """Verify unique constraint prevents duplicate emails within same merchant."""
    merchant = Merchant(name="Merchant One", currency="INR")
    db_session.add(merchant)
    await db_session.flush()

    u1 = User(merchant_id=merchant.id, email="shared@test.local", full_name="User 1")
    db_session.add(u1)
    await db_session.flush()

    u2 = User(merchant_id=merchant.id, email="shared@test.local", full_name="User 2")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_order_payment_and_event_hierarchy(db_session: AsyncSession) -> None:
    """Verify relational hierarchy from Merchant -> Customer -> Order -> Payment -> PaymentEvent."""
    merchant = Merchant(name="Retail Store", currency="INR")
    db_session.add(merchant)
    await db_session.flush()

    customer = Customer(merchant_id=merchant.id, external_customer_id="cust_101", name="Priya")
    db_session.add(customer)
    await db_session.flush()

    order = Order(
        merchant_id=merchant.id,
        customer_id=customer.id,
        external_order_id="ord_101",
        amount=Decimal("4800.50"),
        currency="INR",
        status="ATTEMPTED",
    )
    db_session.add(order)
    await db_session.flush()

    payment = Payment(
        merchant_id=merchant.id,
        order_id=order.id,
        customer_id=customer.id,
        external_payment_id="pay_101",
        amount=Decimal("4800.50"),
        currency="INR",
        status="FAILED",
        payment_method="UPI",
        bank="HDFC",
        error_code="GATEWAY_TIMEOUT",
    )
    db_session.add(payment)
    await db_session.flush()

    event = PaymentEvent(
        merchant_id=merchant.id,
        payment_id=payment.id,
        event_id="evt_webhook_999",
        event_type="payment.failed",
        payload={"reason": "timeout"},
        status="PROCESSED",
    )
    db_session.add(event)
    await db_session.flush()

    assert payment.id is not None
    assert payment.order_id == order.id
    assert payment.amount == Decimal("4800.50")
    assert event.payment_id == payment.id


@pytest.mark.asyncio
async def test_financial_decimal_precision(db_session: AsyncSession) -> None:
    """Verify monetary amounts retain exact Decimal precision without floating-point errors."""
    merchant = Merchant(name="Fintech Store", currency="INR")
    db_session.add(merchant)
    await db_session.flush()

    risk_case = RiskCase(
        merchant_id=merchant.id,
        case_reference="RC-999",
        risk_type="PAYMENT_DEGRADATION",
        title="High Precision Risk Case",
        summary="Testing exact Decimal precision",
        revenue_at_risk=Decimal("840000.00"),
        estimated_recoverable_revenue=Decimal("210000.55"),
        confidence_score=Decimal("0.9125"),
    )
    db_session.add(risk_case)
    await db_session.flush()

    # Query back from database
    result = await db_session.execute(select(RiskCase).where(RiskCase.id == risk_case.id))
    fetched = result.scalar_one()

    assert fetched.revenue_at_risk == Decimal("840000.00")
    assert fetched.estimated_recoverable_revenue == Decimal("210000.55")
    assert fetched.confidence_score == Decimal("0.9125")
    # Verify no float conversion artifacts (e.g. .5500000000001)
    assert str(fetched.revenue_at_risk) == "840000.00"


@pytest.mark.asyncio
async def test_idempotency_key_uniqueness(db_session: AsyncSession) -> None:
    """Verify duplicate idempotency_key triggers an IntegrityError."""
    merchant = Merchant(name="Batch Store", currency="INR")
    db_session.add(merchant)
    await db_session.flush()

    risk_case = RiskCase(
        merchant_id=merchant.id,
        case_reference="RC-101",
        risk_type="PAYMENT_DEGRADATION",
        title="Risk",
        summary="Summary",
    )
    db_session.add(risk_case)
    await db_session.flush()

    plan = RecoveryPlan(
        merchant_id=merchant.id,
        risk_case_id=risk_case.id,
        action_type="PAYMENT_RETRY",
        recommendation="Retry",
    )
    db_session.add(plan)
    await db_session.flush()

    batch1 = RecoveryBatch(
        merchant_id=merchant.id,
        recovery_plan_id=plan.id,
        batch_reference="RB-101",
        idempotency_key="unique_key_12345",
    )
    db_session.add(batch1)
    await db_session.flush()

    batch2 = RecoveryBatch(
        merchant_id=merchant.id,
        recovery_plan_id=plan.id,
        batch_reference="RB-102",
        idempotency_key="unique_key_12345",  # Duplicate key!
    )
    db_session.add(batch2)
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_payment_event_deduplication(db_session: AsyncSession) -> None:
    """Verify duplicate webhook event_id is rejected."""
    merchant = Merchant(name="Webhook Store", currency="INR")
    db_session.add(merchant)
    await db_session.flush()

    evt1 = PaymentEvent(
        merchant_id=merchant.id,
        event_id="evt_duplicate_test_1",
        event_type="payment.captured",
        payload={},
    )
    db_session.add(evt1)
    await db_session.flush()

    evt2 = PaymentEvent(
        merchant_id=merchant.id,
        event_id="evt_duplicate_test_1",  # Duplicate event ID!
        event_type="payment.captured",
        payload={},
    )
    db_session.add(evt2)
    with pytest.raises(IntegrityError):
        await db_session.flush()
