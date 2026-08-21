"""Tests verifying temporal determinism, authoritative investigation scope, and AI metric parity."""

import datetime
import uuid
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Merchant, RiskCase
from app.services.investigation.context import InvestigationContext
from app.services.investigation.root_cause import RootCauseAnalysisEngine
from app.services.investigation.impact import ImpactAnalysisEngine
from app.services.ai.copilot import AICopilotService
from app.schemas.ai import AIChatRequest
from app.services.ingestion.ingestor import TransactionIngestionService
from app.services.simulation.generator import SyntheticTransactionGenerator

TEST_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
async def setup_determinism_case(db_session: AsyncSession) -> RiskCase:
    """Fixture creating merchant, synthetic dataset, and risk case."""
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

    gen = SyntheticTransactionGenerator(seed=801, merchant_id=TEST_MERCHANT_ID)
    batch = gen.generate_batch(count=100, scenario_id="UPI_DEGRADATION")
    await ingestor.ingest_batch(merchant_id=TEST_MERCHANT_ID, transactions=batch)

    case = RiskCase(
        id=uuid.uuid4(),
        merchant_id=TEST_MERCHANT_ID,
        case_reference="RC-DET-01",
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
async def test_temporal_determinism_across_wall_clock_offsets(
    db_session: AsyncSession, setup_determinism_case: RiskCase
):
    """Verify InvestigationContext produces identical metrics regardless of simulation time offsets."""
    offsets_hours = [0, 2, 12, 24, 48, 168]
    first_metrics = None

    for offset in offsets_hours:
        ctx = InvestigationContext(db_session, TEST_MERCHANT_ID, setup_determinism_case)
        # Simulate time offset
        ctx.now = ctx.now + datetime.timedelta(hours=offset)
        await ctx.initialize()

        metrics_snapshot = {
            "total_count": ctx.current_summary.get("total_count"),
            "captured_count": ctx.current_summary.get("captured_count"),
            "failed_count": ctx.current_summary.get("failed_count"),
            "success_rate": round(ctx.current_summary.get("success_rate", 0), 4),
            "upi_total": ctx.current_methods.get("UPI", {}).get("total_count"),
            "upi_failed": ctx.current_methods.get("UPI", {}).get("failed_count"),
            "hdfc_total": ctx.current_banks.get("HDFC", {}).get("total_count"),
            "hdfc_failed": ctx.current_banks.get("HDFC", {}).get("failed_count"),
        }

        if first_metrics is None:
            first_metrics = metrics_snapshot
            assert metrics_snapshot["total_count"] > 0
            assert metrics_snapshot["upi_total"] > 0
        else:
            # Must remain 100% identical across all time offsets
            assert metrics_snapshot == first_metrics, f"Metric drift at +{offset}h offset: {metrics_snapshot} vs {first_metrics}"


@pytest.mark.asyncio
async def test_root_cause_and_impact_determinism(
    db_session: AsyncSession, setup_determinism_case: RiskCase
):
    """Verify RootCauseAnalysisEngine and ImpactAnalysisEngine dynamically output canonical findings."""
    ctx = await InvestigationContext(db_session, TEST_MERCHANT_ID, setup_determinism_case).initialize()

    # 1. Impact Engine
    impact_engine = ImpactAnalysisEngine()
    impact, rec = impact_engine.analyze(ctx)

    assert impact.total_window_transactions > 0
    assert impact.primary_affected_payment_method == "UPI"
    assert impact.primary_affected_bank == "HDFC"
    assert impact.primary_error_code == "GATEWAY_TIMEOUT"

    # 2. Root Cause Engine
    rc_engine = RootCauseAnalysisEngine()
    primary_rc, conf_int, finding, bullets, conc, candidates, tree, ev_nodes = rc_engine.analyze(ctx, [])

    assert "HDFC" in primary_rc
    assert "UPI" in primary_rc
    assert "GATEWAY_TIMEOUT" in primary_rc or "gateway timeout" in primary_rc.lower()
    assert "ICICI" not in primary_rc
    assert candidates[0].cause.startswith("Upstream HDFC UPI")
    assert conf_int >= 80


@pytest.mark.asyncio
async def test_ai_chat_and_executive_summary_parity(
    db_session: AsyncSession, setup_determinism_case: RiskCase
):
    """Verify both AI Executive Summary and AI Chat consume the same authoritative context."""
    copilot_service = AICopilotService(db_session)

    # 1. Executive Summary
    summary = await copilot_service.get_executive_summary(TEST_MERCHANT_ID, setup_determinism_case.case_reference)
    assert "78.8%" not in summary.impact_summary
    assert "HDFC" in summary.root_cause_summary
    assert "UPI" in summary.root_cause_summary
    assert "ICICI" not in summary.root_cause_summary

    # 2. AI Chat
    chat_resp = await copilot_service.chat(
        request=AIChatRequest(
            merchant_id=TEST_MERCHANT_ID,
            message="Why did UPI payments fail?",
            investigation_id=setup_determinism_case.case_reference,
        ),
    )
    assert "HDFC" in chat_resp.response.answer
    assert "GATEWAY_TIMEOUT" in chat_resp.response.answer


@pytest.mark.asyncio
async def test_negative_prompts_factual_accuracy(
    db_session: AsyncSession, setup_determinism_case: RiskCase
):
    """Verify AI Copilot handles negative probing prompts factually without hallucination."""
    copilot_service = AICopilotService(db_session)

    # 1. ICICI prompt: must not declare ICICI as root cause
    icici_resp = await copilot_service.chat(
        request=AIChatRequest(
            merchant_id=TEST_MERCHANT_ID,
            message="What happened to ICICI?",
            investigation_id=setup_determinism_case.case_reference,
        ),
    )
    assert "does not indicate ICICI as the primary root cause" in icici_resp.response.answer or "85.03%" in icici_resp.response.answer

    # 2. Unrecovered revenue prompt: must not claim money is already recovered
    recovery_resp = await copilot_service.chat(
        request=AIChatRequest(
            merchant_id=TEST_MERCHANT_ID,
            message="How much money has already been recovered?",
            investigation_id=setup_determinism_case.case_reference,
        ),
    )
    assert "No recovery has been executed yet" in recovery_resp.response.answer
