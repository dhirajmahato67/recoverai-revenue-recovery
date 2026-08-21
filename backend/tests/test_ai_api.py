"""Integration tests for Phase 6 AI Copilot API endpoints."""

import datetime
import uuid
from decimal import Decimal
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Merchant, RiskCase
from app.services.ingestion.ingestor import TransactionIngestionService
from app.services.simulation.generator import SyntheticTransactionGenerator

TEST_MERCHANT_ID = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
async def setup_ai_api_case(db_session: AsyncSession) -> RiskCase:
    """Fixture ensuring merchant, payments, and risk case exist in database."""
    uid = uuid.UUID(TEST_MERCHANT_ID)
    merchant = await db_session.get(Merchant, uid)
    if not merchant:
        merchant = Merchant(
            id=uid,
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

    gen = SyntheticTransactionGenerator(seed=701, merchant_id=uid)
    batch = gen.generate_batch(count=80, scenario_id="UPI_DEGRADATION")
    await ingestor.ingest_batch(merchant_id=uid, transactions=batch)

    case = RiskCase(
        id=uuid.uuid4(),
        merchant_id=uid,
        case_reference="RC-AI-01",
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
async def test_ai_status_endpoint(client: AsyncClient):
    """Test GET /api/v1/ai/status probe."""
    resp = await client.get("/api/v1/ai/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["enabled"] is True
    assert "provider" in data
    assert "mode" in data
    assert data["healthy"] is True


@pytest.mark.asyncio
async def test_ai_chat_root_cause_question(client: AsyncClient, setup_ai_api_case: RiskCase):
    """Test POST /api/v1/ai/chat with root cause question."""
    case_ref = setup_ai_api_case.case_reference
    payload = {
        "investigation_id": case_ref,
        "message": "Why did UPI payments fail?",
        "merchant_id": TEST_MERCHANT_ID,
    }
    resp = await client.post("/api/v1/ai/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["investigation_id"] == case_ref
    assert data["provider"] in ("mock", "openai")
    assert data["latency_ms"] >= 0

    res_payload = data["response"]
    assert "HDFC" in res_payload["answer"]
    assert "64.77%" in res_payload["answer"] or "UPI" in res_payload["answer"]
    assert res_payload["response_type"] in ("ROOT_CAUSE", "EXPLANATION")
    assert res_payload["confidence"] > 0.5
    assert len(res_payload["evidence_refs"]) > 0
    assert res_payload["can_execute_action"] is False


@pytest.mark.asyncio
async def test_ai_chat_financial_impact_question(client: AsyncClient, setup_ai_api_case: RiskCase):
    """Test POST /api/v1/ai/chat with financial impact question."""
    case_ref = setup_ai_api_case.case_reference
    payload = {
        "investigation_id": case_ref,
        "message": "How much revenue is at risk?",
        "merchant_id": TEST_MERCHANT_ID,
    }
    resp = await client.post("/api/v1/ai/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    res_payload = data["response"]

    assert "1,219,544.00" in res_payload["answer"]
    assert "304,886.00" in res_payload["answer"]
    assert res_payload["response_type"] == "IMPACT"


@pytest.mark.asyncio
async def test_ai_chat_recommendation_question(client: AsyncClient, setup_ai_api_case: RiskCase):
    """Test POST /api/v1/ai/chat proposing bounded action without direct execution."""
    case_ref = setup_ai_api_case.case_reference
    payload = {
        "investigation_id": case_ref,
        "message": "What should we do next to recover revenue?",
        "merchant_id": TEST_MERCHANT_ID,
    }
    resp = await client.post("/api/v1/ai/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    res_payload = data["response"]

    assert len(res_payload["recommended_actions"]) > 0
    action = res_payload["recommended_actions"][0]
    assert action["action"] == "PAYMENT_RETRY"
    assert action["requires_approval"] is True
    assert action["can_execute"] is False
    assert res_payload["can_execute_action"] is False


@pytest.mark.asyncio
async def test_ai_executive_summary_endpoint(client: AsyncClient, setup_ai_api_case: RiskCase):
    """Test GET /api/v1/ai/investigations/{id}/summary."""
    case_ref = setup_ai_api_case.case_reference
    resp = await client.get(f"/api/v1/ai/investigations/{case_ref}/summary?merchant_id={TEST_MERCHANT_ID}")
    assert resp.status_code == 200
    data = resp.json()

    assert data["investigation_id"] == case_ref
    assert "UPI" in data["incident_title"]
    assert "1,219,544.00" in data["impact_summary"]
    assert data["confidence_score"] > 0.5
    assert len(data["evidence_summary"]) >= 3
    assert data["requires_approval"] is True

