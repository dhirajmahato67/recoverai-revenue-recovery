"""Deterministic, idempotent seed script for Acme Commerce demonstration dataset."""

import asyncio
import datetime
import random
import uuid
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger, setup_logging
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
    Approval,
    AuditLog,
    AgentRun,
    AgentToolCall,
)
from app.db.session import get_session_factory

logger = get_logger("app.db.seed")

# Deterministic UUIDs for primary entities
ACME_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
ACME_ADMIN_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
PRIMARY_RISK_CASE_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
PRIMARY_INVESTIGATION_ID = uuid.UUID("00000000-0000-0000-0000-000000000020")
PRIMARY_PLAN_ID = uuid.UUID("00000000-0000-0000-0000-000000000030")
PRIMARY_BATCH_ID = uuid.UUID("00000000-0000-0000-0000-000000000040")
PRIMARY_APPROVAL_ID = uuid.UUID("00000000-0000-0000-0000-000000000050")
PRIMARY_AGENT_RUN_ID = uuid.UUID("00000000-0000-0000-0000-000000000060")

CUSTOMER_NAMES = [
    ("Aarav Sharma", "aarav.sharma@example.local", "9182"),
    ("Priya Mehta", "priya.mehta@example.local", "8271"),
    ("Rahul Verma", "rahul.verma@example.local", "7362"),
    ("Ananya Singh", "ananya.singh@example.local", "6453"),
    ("Rohan Gupta", "rohan.gupta@example.local", "5544"),
    ("Neha Patel", "neha.patel@example.local", "4635"),
    ("Aditya Rao", "aditya.rao@example.local", "3726"),
    ("Sneha Iyer", "sneha.iyer@example.local", "2817"),
    ("Kabir Joshi", "kabir.joshi@example.local", "1908"),
    ("Pooja Nair", "pooja.nair@example.local", "9019"),
    ("Vikram Malhotra", "vikram.malhotra@example.local", "8120"),
    ("Ishita Roy", "ishita.roy@example.local", "7231"),
    ("Arjun Kapoor", "arjun.kapoor@example.local", "6342"),
    ("Kavya Pillai", "kavya.pillai@example.local", "5453"),
    ("Varun Deshmukh", "varun.deshmukh@example.local", "4564"),
    ("Divya Menon", "divya.menon@example.local", "3675"),
    ("Sameer Saxena", "sameer.saxena@example.local", "2786"),
    ("Tanvi Kulkarni", "tanvi.kulkarni@example.local", "1897"),
    ("Manoj Choudhary", "manoj.choudhary@example.local", "9908"),
    ("Ritu Banerjee", "ritu.banerjee@example.local", "8819"),
    ("Deepak Bhatt", "deepak.bhatt@example.local", "7720"),
    ("Swati Sengupta", "swati.sengupta@example.local", "6631"),
    ("Nitin Agarwal", "nitin.agarwal@example.local", "5542"),
    ("Meera Nambiar", "meera.nambiar@example.local", "4453"),
    ("Siddharth Ghosh", "siddharth.ghosh@example.local", "3364"),
]


async def seed_database(session: AsyncSession) -> None:
    """Execute deterministic, idempotent database seeding."""
    logger.info("Starting database seeding...")

    # 1. Seed Merchant
    merchant = await session.get(Merchant, ACME_MERCHANT_ID)
    if not merchant:
        merchant = Merchant(
            id=ACME_MERCHANT_ID,
            name="Acme Commerce",
            legal_name="Acme Digital Retail Technologies Pvt Ltd",
            currency="INR",
            timezone="Asia/Kolkata",
            status="ACTIVE",
            external_reference="acme_commerce",
        )
        session.add(merchant)
        await session.flush()
        logger.info(f"Seeded merchant: {merchant.name}")
    else:
        logger.info(f"Merchant {merchant.name} already exists.")

    # 2. Seed Users
    users_data = [
        (ACME_ADMIN_USER_ID, "admin@acme-demo.local", "Aarav Sharma (Admin)", "ADMIN"),
        (uuid.UUID("00000000-0000-0000-0000-000000000003"), "analyst@acme-demo.local", "Priya Mehta (Analyst)", "ANALYST"),
        (uuid.UUID("00000000-0000-0000-0000-000000000004"), "merchant@acme-demo.local", "Vikram Malhotra (Ops)", "MERCHANT"),
    ]
    for uid, email, full_name, role in users_data:
        existing_user = await session.execute(
            select(User).where(User.merchant_id == ACME_MERCHANT_ID, User.email == email)
        )
        if not existing_user.scalar_one_or_none():
            user = User(id=uid, merchant_id=ACME_MERCHANT_ID, email=email, full_name=full_name, role=role, status="ACTIVE")
            session.add(user)
    await session.flush()

    # 3. Seed Customers
    customer_entities: list[Customer] = []
    for i, (c_name, c_email, c_phone) in enumerate(CUSTOMER_NAMES):
        ext_cust_id = f"cust_acme_{i+1:04d}"
        cust_stmt = select(Customer).where(Customer.merchant_id == ACME_MERCHANT_ID, Customer.external_customer_id == ext_cust_id)
        cust = (await session.execute(cust_stmt)).scalar_one_or_none()
        if not cust:
            cust = Customer(
                merchant_id=ACME_MERCHANT_ID,
                external_customer_id=ext_cust_id,
                name=c_name,
                email=c_email,
                phone_last4=c_phone,
                status="ACTIVE",
            )
            session.add(cust)
            await session.flush()
        customer_entities.append(cust)

    # 4. Seed 350 Synthetic Orders and Payments (supporting HDFC UPI degradation scenario)
    # Using fixed seed for PRNG determinism
    prng = random.Random(42)
    now = datetime.datetime.now(datetime.timezone.utc)

    existing_payments_count = (await session.execute(select(Payment).where(Payment.merchant_id == ACME_MERCHANT_ID))).scalars().all()
    if len(existing_payments_count) < 100:
        logger.info("Seeding synthetic transactions...")
        # Exact 100% distribution: 60% UPI (15), 20% Card (5), 12% Net Banking (3), 8% Wallet (2) = 25 items (100.0%)
        payment_methods = (
            ["UPI"] * 15 +
            ["CARD"] * 5 +
            ["NETBANKING"] * 3 +
            ["WALLET"] * 2
        )
        # Bank distribution: 40% HDFC, 25% ICICI, 20% SBI, 15% AXIS = 20 items (100.0%)
        banks = (
            ["HDFC"] * 8 +
            ["ICICI"] * 5 +
            ["SBI"] * 4 +
            ["AXIS"] * 3
        )
        amounts = [
            Decimal("999.00"), Decimal("1499.00"), Decimal("2450.00"),
            Decimal("3200.00"), Decimal("4800.00"), Decimal("7500.00"), Decimal("12500.00")
        ]

        for i in range(1, 351):
            ext_order_id = f"ord_acme_{i:05d}"
            ext_payment_id = f"pay_acme_{i:05d}"
            customer = prng.choice(customer_entities)
            amount = prng.choice(amounts)
            method = prng.choice(payment_methods)
            bank = prng.choice(banks)

            # Determine failure based on scenario: HDFC UPI has higher failure rate
            if method == "UPI" and bank == "HDFC":
                is_failed = prng.random() < 0.311  # 31.1% failure rate for HDFC UPI
            elif method == "UPI":
                is_failed = prng.random() < 0.080  # 8.0% failure rate for other UPI
            else:
                is_failed = prng.random() < 0.045  # 4.5% failure rate for cards/netbanking

            status = "FAILED" if is_failed else "CAPTURED"
            error_code = "GATEWAY_TIMEOUT" if is_failed and prng.random() < 0.6 else ("BANK_DECLINED" if is_failed else None)
            error_reason = "Issuer bank timeout on UPI response" if error_code == "GATEWAY_TIMEOUT" else ("Transaction declined by customer bank" if is_failed else None)

            # Order
            order = Order(
                merchant_id=ACME_MERCHANT_ID,
                customer_id=customer.id,
                external_order_id=ext_order_id,
                amount=amount,
                currency="INR",
                status="PAID" if status == "CAPTURED" else "FAILED",
                description=f"Standard retail purchase item #{i}",
            )
            session.add(order)
            await session.flush()

            # Payment
            payment = Payment(
                merchant_id=ACME_MERCHANT_ID,
                order_id=order.id,
                customer_id=customer.id,
                external_payment_id=ext_payment_id,
                amount=amount,
                currency="INR",
                status=status,
                payment_method=method,
                bank=bank,
                error_code=error_code,
                error_reason=error_reason,
                captured_at=now - datetime.timedelta(minutes=prng.randint(10, 1440)) if status == "CAPTURED" else None,
            )
            session.add(payment)
            await session.flush()

            # PaymentEvent
            event = PaymentEvent(
                merchant_id=ACME_MERCHANT_ID,
                payment_id=payment.id,
                event_id=f"evt_acme_{i:05d}",
                event_type="payment.captured" if status == "CAPTURED" else "payment.failed",
                payload={
                    "payment_id": ext_payment_id,
                    "order_id": ext_order_id,
                    "amount": float(amount),
                    "currency": "INR",
                    "status": status.lower(),
                    "method": method.lower(),
                    "bank": bank,
                    "error_code": error_code,
                },
                signature_valid=True,
                status="PROCESSED",
            )
            session.add(event)

        await session.flush()
        logger.info("Seeded 350 synthetic orders, payments, and event records.")

    # 5. Seed Primary Demo Risk Case (RC-001: UPI Degradation)
    risk_case = await session.get(RiskCase, PRIMARY_RISK_CASE_ID)
    if not risk_case:
        risk_case = RiskCase(
            id=PRIMARY_RISK_CASE_ID,
            merchant_id=ACME_MERCHANT_ID,
            case_reference="RC-001",
            risk_type="PAYMENT_DEGRADATION",
            severity="HIGH",
            status="OPEN",
            title="UPI payment degradation",
            summary="Payment success rate has significantly declined compared with baseline, with HDFC UPI contributing the largest observed degradation.",
            revenue_at_risk=Decimal("840000.00"),
            estimated_recoverable_revenue=Decimal("210000.00"),
            confidence_score=Decimal("0.9100"),
            detected_at=now - datetime.timedelta(hours=2),
        )
        session.add(risk_case)
        await session.flush()

        # Risk Signals
        signals = [
            RiskSignal(
                risk_case_id=PRIMARY_RISK_CASE_ID,
                signal_type="METRIC_ANOMALY",
                metric_name="payment_success_rate",
                baseline_value=Decimal("0.9420"),
                observed_value=Decimal("0.8170"),
                deviation_value=Decimal("-0.1250"),
                dimension="overall",
                dimension_value="all_methods",
                evidence={"window": "2h", "sample_size": 438, "impact": "High drop in checkout conversions"},
            ),
            RiskSignal(
                risk_case_id=PRIMARY_RISK_CASE_ID,
                signal_type="DIMENSION_BREAKDOWN",
                metric_name="method_success_rate",
                baseline_value=Decimal("0.9310"),
                observed_value=Decimal("0.7420"),
                deviation_value=Decimal("-0.1890"),
                dimension="payment_method",
                dimension_value="UPI",
                evidence={"method": "UPI", "share_of_traffic": 0.62},
            ),
            RiskSignal(
                risk_case_id=PRIMARY_RISK_CASE_ID,
                signal_type="ROOT_CAUSE_ISOLATION",
                metric_name="bank_success_rate",
                baseline_value=Decimal("0.9400"),
                observed_value=Decimal("0.6890"),
                deviation_value=Decimal("-0.2510"),
                dimension="bank",
                dimension_value="HDFC",
                evidence={"bank": "HDFC", "error_code": "GATEWAY_TIMEOUT", "latency_spike_p95_ms": 8400},
            ),
        ]
        session.add_all(signals)
        await session.flush()
        logger.info("Seeded primary RiskCase RC-001 and supporting signals.")

    # 6. Seed Investigation (INV-001)
    investigation = await session.get(Investigation, PRIMARY_INVESTIGATION_ID)
    if not investigation:
        investigation = Investigation(
            id=PRIMARY_INVESTIGATION_ID,
            risk_case_id=PRIMARY_RISK_CASE_ID,
            status="COMPLETED",
            summary="UPI degradation is the primary observed contributor to the payment success-rate decline.",
            root_cause="HDFC UPI gateway latency spike and timeout degradation during peak noon window.",
            confidence_score=Decimal("0.9100"),
            started_at=now - datetime.timedelta(hours=2),
            completed_at=now - datetime.timedelta(hours=1, minutes=50),
        )
        session.add(investigation)
        await session.flush()
        logger.info("Seeded Investigation INV-001.")

    # 7. Seed Recovery Plan (PLAN-001)
    plan = await session.get(RecoveryPlan, PRIMARY_PLAN_ID)
    if not plan:
        plan = RecoveryPlan(
            id=PRIMARY_PLAN_ID,
            merchant_id=ACME_MERCHANT_ID,
            risk_case_id=PRIMARY_RISK_CASE_ID,
            action_type="PAYMENT_RETRY",
            estimated_recovery=Decimal("210000.00"),
            maximum_exposure=Decimal("210000.00"),
            max_retries=1,
            failure_threshold=Decimal("0.3000"),
            eligible_transaction_count=438,
            status="PENDING_APPROVAL",
            recommendation="Dispatch smart single-retry workflow across 438 eligible HDFC UPI timeout transactions with 30% circuit-breaker stop threshold.",
            created_by=ACME_ADMIN_USER_ID,
        )
        session.add(plan)
        await session.flush()

    # 8. Seed Recovery Batch (RB-001)
    batch = await session.get(RecoveryBatch, PRIMARY_BATCH_ID)
    if not batch:
        batch = RecoveryBatch(
            id=PRIMARY_BATCH_ID,
            merchant_id=ACME_MERCHANT_ID,
            recovery_plan_id=PRIMARY_PLAN_ID,
            batch_reference="RB-001",
            status="PENDING_APPROVAL",
            total_transactions=438,
            eligible_transactions=438,
            attempted_transactions=0,
            successful_transactions=0,
            failed_transactions=0,
            skipped_transactions=0,
            estimated_recovery=Decimal("210000.00"),
            actual_recovery=Decimal("0.00"),
            idempotency_key="idem_rb001_acme_20260821",
        )
        session.add(batch)
        await session.flush()

    # 9. Seed Approval (APP-001)
    approval = await session.get(Approval, PRIMARY_APPROVAL_ID)
    if not approval:
        approval = Approval(
            id=PRIMARY_APPROVAL_ID,
            merchant_id=ACME_MERCHANT_ID,
            recovery_plan_id=PRIMARY_PLAN_ID,
            requested_by=ACME_ADMIN_USER_ID,
            status="PENDING",
            reason="Merchant admin authorization required before executing financial retry batch.",
            requested_at=now - datetime.timedelta(hours=1, minutes=45),
        )
        session.add(approval)
        await session.flush()

    # 10. Seed Audit Logs
    existing_logs = (await session.execute(select(AuditLog).where(AuditLog.merchant_id == ACME_MERCHANT_ID))).scalars().all()
    if len(existing_logs) == 0:
        audit_events = [
            AuditLog(
                merchant_id=ACME_MERCHANT_ID,
                actor_type="AI_AGENT",
                actor_id="diagnostics_agent_v1",
                action="RISK_DETECTED",
                resource_type="RiskCase",
                resource_id="RC-001",
                request_id="req_diag_1039",
                metadata_={"severity": "HIGH", "risk_type": "PAYMENT_DEGRADATION", "revenue_at_risk": 840000.0},
            ),
            AuditLog(
                merchant_id=ACME_MERCHANT_ID,
                actor_type="AI_AGENT",
                actor_id="diagnostics_agent_v1",
                action="INVESTIGATION_COMPLETED",
                resource_type="Investigation",
                resource_id="INV-001",
                request_id="req_diag_1040",
                metadata_={"root_cause": "HDFC UPI Latency", "confidence": 0.91},
            ),
            AuditLog(
                merchant_id=ACME_MERCHANT_ID,
                actor_type="POLICY_ENGINE",
                actor_id="policy_engine_v1",
                action="RECOVERY_RECOMMENDED",
                resource_type="RecoveryPlan",
                resource_id="PLAN-001",
                request_id="req_policy_201",
                metadata_={"max_retries": 1, "failure_threshold": 0.30, "exposure_cap": 210000.0},
            ),
            AuditLog(
                merchant_id=ACME_MERCHANT_ID,
                actor_type="POLICY_ENGINE",
                actor_id="policy_engine_v1",
                action="POLICY_VALIDATED",
                resource_type="RecoveryPlan",
                resource_id="PLAN-001",
                request_id="req_policy_202",
                metadata_={"duplicate_check": "PASSED", "exposure_check": "PASSED", "approval_required": True},
            ),
        ]
        session.add_all(audit_events)
        await session.flush()

    # 11. Seed Agent Run & Tool Calls
    agent_run = await session.get(AgentRun, PRIMARY_AGENT_RUN_ID)
    if not agent_run:
        agent_run = AgentRun(
            id=PRIMARY_AGENT_RUN_ID,
            merchant_id=ACME_MERCHANT_ID,
            risk_case_id=PRIMARY_RISK_CASE_ID,
            model="gemini-2.0-flash",
            prompt_version="v1.0",
            status="COMPLETED",
            latency_ms=1420,
            started_at=now - datetime.timedelta(hours=2),
            completed_at=now - datetime.timedelta(hours=1, minutes=58),
        )
        session.add(agent_run)
        await session.flush()

        tool_calls = [
            AgentToolCall(
                agent_run_id=PRIMARY_AGENT_RUN_ID,
                tool_name="get_case_details",
                arguments={"case_reference": "RC-001"},
                result={"risk_type": "PAYMENT_DEGRADATION", "detected_drop": "12.5pp"},
                status="COMPLETED",
                latency_ms=140,
            ),
            AgentToolCall(
                agent_run_id=PRIMARY_AGENT_RUN_ID,
                tool_name="analyze_payment_degradation",
                arguments={"time_window": "2h", "merchant_id": str(ACME_MERCHANT_ID)},
                result={"primary_method": "UPI", "method_drop": "18.9pp"},
                status="COMPLETED",
                latency_ms=380,
            ),
            AgentToolCall(
                agent_run_id=PRIMARY_AGENT_RUN_ID,
                tool_name="get_root_cause",
                arguments={"dimension": "bank", "filter": "UPI"},
                result={"bank": "HDFC", "error_code": "GATEWAY_TIMEOUT", "p95_latency_ms": 8400},
                status="COMPLETED",
                latency_ms=510,
            ),
            AgentToolCall(
                agent_run_id=PRIMARY_AGENT_RUN_ID,
                tool_name="calculate_recovery_estimate",
                arguments={"eligible_transactions": 438, "expected_success_rate": 0.42},
                result={"recoverable_inr": 210000.0, "confidence": 0.91},
                status="COMPLETED",
                latency_ms=190,
            ),
        ]
        session.add_all(tool_calls)
        await session.flush()

    await session.commit()
    logger.info("Database seeding completed successfully!")


async def main() -> None:
    """CLI entry point for running database seeding."""
    setup_logging()
    factory = get_session_factory()
    async with factory() as session:
        await seed_database(session)


if __name__ == "__main__":
    asyncio.run(main())
