"""Tests verifying strict multi-tenant scoping and cross-tenant data isolation."""

from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Merchant, Customer, Order, Payment, RiskCase
from app.db.repositories import PaymentRepository, RiskCaseRepository, CustomerRepository


@pytest.mark.asyncio
async def test_tenant_data_isolation(db_session: AsyncSession) -> None:
    """Verify that tenant queries for Merchant A cannot access Merchant B records."""
    # 1. Create Merchant A & B
    merchant_a = Merchant(name="Merchant Alpha", currency="INR")
    merchant_b = Merchant(name="Merchant Beta", currency="INR")
    db_session.add_all([merchant_a, merchant_b])
    await db_session.flush()

    # 2. Create Customers
    cust_a = Customer(merchant_id=merchant_a.id, external_customer_id="cust_001", name="Alpha Customer")
    cust_b = Customer(merchant_id=merchant_b.id, external_customer_id="cust_001", name="Beta Customer")
    db_session.add_all([cust_a, cust_b])
    await db_session.flush()

    # 3. Create Orders & Payments
    ord_a = Order(merchant_id=merchant_a.id, customer_id=cust_a.id, external_order_id="ord_001", amount=Decimal("1000.00"))
    ord_b = Order(merchant_id=merchant_b.id, customer_id=cust_b.id, external_order_id="ord_001", amount=Decimal("2000.00"))
    db_session.add_all([ord_a, ord_b])
    await db_session.flush()

    pay_a = Payment(
        merchant_id=merchant_a.id,
        order_id=ord_a.id,
        customer_id=cust_a.id,
        external_payment_id="pay_001",
        amount=Decimal("1000.00"),
        status="CAPTURED",
        payment_method="UPI",
    )
    pay_b = Payment(
        merchant_id=merchant_b.id,
        order_id=ord_b.id,
        customer_id=cust_b.id,
        external_payment_id="pay_001",
        amount=Decimal("2000.00"),
        status="FAILED",
        payment_method="CARD",
    )
    db_session.add_all([pay_a, pay_b])
    await db_session.flush()

    # 4. Initialize Repositories
    payment_repo = PaymentRepository(db_session)
    customer_repo = CustomerRepository(db_session)

    # 5. Verify Scoped Retrieval: querying for Merchant A with Pay B's ID must return None
    cross_tenant_payment = await payment_repo.get_by_id_scoped(merchant_a.id, pay_b.id)
    assert cross_tenant_payment is None, "Security violation: Merchant A was able to access Merchant B payment!"

    # Correct tenant query must succeed
    valid_payment_a = await payment_repo.get_by_id_scoped(merchant_a.id, pay_a.id)
    assert valid_payment_a is not None
    assert valid_payment_a.amount == Decimal("1000.00")

    # 6. Verify Scoped List: list_scoped for Merchant A must return exactly 1 payment
    merchant_a_payments = await payment_repo.list_scoped(merchant_a.id)
    assert len(merchant_a_payments) == 1
    assert merchant_a_payments[0].id == pay_a.id

    merchant_b_payments = await payment_repo.list_scoped(merchant_b.id)
    assert len(merchant_b_payments) == 1
    assert merchant_b_payments[0].id == pay_b.id
