"""Tests verifying repository queries, filtering, and pagination."""

from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Merchant,
    Customer,
    Order,
    Payment,
    RiskCase,
    RiskSignal,
    Investigation,
    RecoveryPlan,
    RecoveryBatch,
)
from app.db.repositories import (
    MerchantRepository,
    CustomerRepository,
    PaymentRepository,
    RiskCaseRepository,
    RecoveryBatchRepository,
    AuditLogRepository,
)


@pytest.mark.asyncio
async def test_payment_repository_filtering_and_pagination(db_session: AsyncSession) -> None:
    """Verify payment filtering by status and method, plus pagination limits."""
    merchant = Merchant(name="E-Commerce Corp", currency="INR")
    db_session.add(merchant)
    await db_session.flush()

    customer = Customer(merchant_id=merchant.id, external_customer_id="cust_p1")
    db_session.add(customer)
    await db_session.flush()

    order = Order(merchant_id=merchant.id, customer_id=customer.id, external_order_id="ord_p1", amount=Decimal("100.00"))
    db_session.add(order)
    await db_session.flush()

    # Create 15 payments: 10 UPI (5 captured, 5 failed), 5 CARD (all captured)
    payments = []
    for i in range(1, 11):
        payments.append(
            Payment(
                merchant_id=merchant.id,
                order_id=order.id,
                customer_id=customer.id,
                external_payment_id=f"pay_filter_{i}",
                amount=Decimal("1500.00"),
                status="CAPTURED" if i <= 5 else "FAILED",
                payment_method="UPI",
                bank="HDFC",
            )
        )
    for i in range(11, 16):
        payments.append(
            Payment(
                merchant_id=merchant.id,
                order_id=order.id,
                customer_id=customer.id,
                external_payment_id=f"pay_filter_{i}",
                amount=Decimal("2500.00"),
                status="CAPTURED",
                payment_method="CARD",
                bank="ICICI",
            )
        )
    db_session.add_all(payments)
    await db_session.flush()

    repo = PaymentRepository(db_session)

    # Test filtering by status=FAILED
    failed_payments = await repo.list_payments_filtered(merchant.id, status="FAILED")
    assert len(failed_payments) == 5

    # Test filtering by payment_method=CARD
    card_payments = await repo.list_payments_filtered(merchant.id, payment_method="CARD")
    assert len(card_payments) == 5

    # Test pagination: page 1 of size 10
    page_items, total_count = await repo.paginate_scoped(merchant.id, page=1, page_size=10)
    assert total_count == 15
    assert len(page_items) == 10

    # Test pagination: page 2 of size 10
    page2_items, total_count = await repo.paginate_scoped(merchant.id, page=2, page_size=10)
    assert total_count == 15
    assert len(page2_items) == 5


@pytest.mark.asyncio
async def test_risk_case_repository_eager_loading(db_session: AsyncSession) -> None:
    """Verify RiskCaseRepository.get_with_details eagerly loads signals and investigations."""
    merchant = Merchant(name="Telemetry Merchant", currency="INR")
    db_session.add(merchant)
    await db_session.flush()

    case = RiskCase(
        merchant_id=merchant.id,
        case_reference="RC-101",
        risk_type="PAYMENT_DEGRADATION",
        title="UPI Anomaly",
        summary="Degradation detected",
        revenue_at_risk=Decimal("500000.00"),
        estimated_recoverable_revenue=Decimal("150000.00"),
    )
    db_session.add(case)
    await db_session.flush()

    signal = RiskSignal(
        risk_case_id=case.id,
        signal_type="ANOMALY",
        metric_name="success_rate",
        evidence={"drop": 0.15},
    )
    investigation = Investigation(
        risk_case_id=case.id,
        status="COMPLETED",
        summary="Root cause summary",
        root_cause="HDFC Gateway",
    )
    db_session.add_all([signal, investigation])
    await db_session.flush()

    repo = RiskCaseRepository(db_session)
    loaded = await repo.get_with_details(merchant.id, case.id)

    assert loaded is not None
    assert len(loaded.signals) == 1
    assert len(loaded.investigations) == 1
    assert loaded.investigations[0].root_cause == "HDFC Gateway"


@pytest.mark.asyncio
async def test_audit_log_repository_record_and_list(db_session: AsyncSession) -> None:
    """Verify AuditLogRepository records immutable ledger entries and retrieves by resource."""
    merchant = Merchant(name="Audit Merchant", currency="INR")
    db_session.add(merchant)
    await db_session.flush()

    repo = AuditLogRepository(db_session)
    await repo.record_event(
        merchant_id=merchant.id,
        actor_type="POLICY_ENGINE",
        action="POLICY_VALIDATED",
        resource_type="RecoveryBatch",
        resource_id="RB-001",
        metadata={"status": "PASSED"},
    )

    logs = await repo.list_for_resource(merchant.id, resource_type="RecoveryBatch", resource_id="RB-001")
    assert len(logs) == 1
    assert logs[0].action == "POLICY_VALIDATED"
    assert logs[0].metadata_["status"] == "PASSED"
