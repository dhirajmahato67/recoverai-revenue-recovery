"""Integration tests for all Phase 4 FastAPI REST endpoints."""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Merchant

TEST_MERCHANT_ID = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
async def ensure_merchant(db_session: AsyncSession):
    """Seed test merchant."""
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
    return merchant


@pytest.mark.asyncio
async def test_get_simulation_scenarios(client: AsyncClient):
    """GET /api/v1/simulation/scenarios returns scenario list."""
    response = await client.get("/api/v1/simulation/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    ids = [s["id"] for s in data]
    assert "NORMAL_BASELINE" in ids
    assert "UPI_DEGRADATION" in ids


@pytest.mark.asyncio
async def test_post_simulation_generate(client: AsyncClient, ensure_merchant):
    """POST /api/v1/simulation/generate generates transactions with deterministic seed."""
    payload = {
        "merchant_id": TEST_MERCHANT_ID,
        "count": 25,
        "scenario": "UPI_DEGRADATION",
        "seed": 42,
        "persist": True,
    }
    response = await client.post("/api/v1/simulation/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 25
    assert data["scenario"] == "UPI_DEGRADATION"
    assert data["persisted"] is True
    assert len(data["sample_transactions"]) > 0


@pytest.mark.asyncio
async def test_transactions_endpoints(client: AsyncClient, ensure_merchant):
    """Test ingestion, querying, and single retrieval of transactions."""
    # 1. Ingest batch
    batch_payload = {
        "merchant_id": TEST_MERCHANT_ID,
        "transactions": [
            {
                "merchant_id": TEST_MERCHANT_ID,
                "external_order_id": "ord_api_01",
                "external_payment_id": "pay_api_01",
                "external_customer_id": "cust_api_01",
                "customer_name": "Rohan Gupta",
                "customer_email": "rohan@example.local",
                "amount": "1499.00",
                "currency": "INR",
                "status": "CAPTURED",
                "payment_method": "UPI",
                "bank": "HDFC",
            },
            {
                "merchant_id": TEST_MERCHANT_ID,
                "external_order_id": "ord_api_02",
                "external_payment_id": "pay_api_02",
                "external_customer_id": "cust_api_02",
                "customer_name": "Sneha Iyer",
                "customer_email": "sneha@example.local",
                "amount": "2450.00",
                "currency": "INR",
                "status": "FAILED",
                "payment_method": "UPI",
                "bank": "HDFC",
                "error_code": "GATEWAY_TIMEOUT",
                "error_reason": "Issuer bank timeout",
            },
        ],
    }
    ingest_res = await client.post("/api/v1/transactions/ingest/batch", json=batch_payload)
    assert ingest_res.status_code == 200
    assert ingest_res.json()["accepted"] == 2

    # 2. List transactions
    list_res = await client.get(f"/api/v1/transactions?merchant_id={TEST_MERCHANT_ID}&pageSize=10")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 2
    assert len(list_data["items"]) >= 2

    # 3. Get single transaction
    get_res = await client.get(f"/api/v1/transactions/pay_api_01?merchant_id={TEST_MERCHANT_ID}")
    assert get_res.status_code == 200
    tx_data = get_res.json()
    assert tx_data["id"] == "pay_api_01"
    assert tx_data["method"] == "UPI"
    assert len(tx_data["timeline"]) > 0


@pytest.mark.asyncio
async def test_risk_analysis_and_cases_endpoints(client: AsyncClient, ensure_merchant):
    """Test risk analysis trigger, cases listing, and metrics retrieval."""
    # 1. Trigger risk analysis
    analysis_res = await client.post(
        "/api/v1/risk/analyze",
        json={"merchant_id": TEST_MERCHANT_ID, "current_window_minutes": 120, "dry_run": False},
    )
    assert analysis_res.status_code == 200
    res_data = analysis_res.json()
    assert "composite_risk_score" in res_data
    assert "severity" in res_data

    # 2. Query risk cases
    cases_res = await client.get(f"/api/v1/risk/cases?merchant_id={TEST_MERCHANT_ID}")
    assert cases_res.status_code == 200
    assert isinstance(cases_res.json(), list)

    # 3. Query risk metrics
    metrics_res = await client.get(f"/api/v1/risk/metrics?merchant_id={TEST_MERCHANT_ID}")
    assert metrics_res.status_code == 200
    assert "overall_health_score" in metrics_res.json()


@pytest.mark.asyncio
async def test_dashboard_metrics_endpoint(client: AsyncClient, ensure_merchant):
    """GET /api/v1/dashboard/metrics returns compliant dashboard payload."""
    dash_res = await client.get(f"/api/v1/dashboard/metrics?merchant_id={TEST_MERCHANT_ID}&timeframe=24h")
    assert dash_res.status_code == 200
    data = dash_res.json()
    assert "revenueAtRisk" in data
    assert "recoverableRevenue" in data
    assert "paymentSuccessRate" in data
    assert "paymentMethods" in data
    assert "trendData" in data


@pytest.mark.asyncio
async def test_pipeline_status_and_run_endpoints(client: AsyncClient, ensure_merchant):
    """Test pipeline status, metrics, and full run execution."""
    # Pipeline status
    status_res = await client.get(f"/api/v1/pipeline/status?merchant_id={TEST_MERCHANT_ID}")
    assert status_res.status_code == 200
    assert "status" in status_res.json()

    # Pipeline metrics
    metrics_res = await client.get(f"/api/v1/pipeline/metrics?merchant_id={TEST_MERCHANT_ID}")
    assert metrics_res.status_code == 200
    assert "total_database_records" in metrics_res.json()

    # Pipeline run
    run_res = await client.post(
        "/api/v1/pipeline/run",
        json={"merchant_id": TEST_MERCHANT_ID, "scenario": "UPI_DEGRADATION", "count": 50, "seed": 77},
    )
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["total_generated"] == 50
    assert run_data["ingestion"]["accepted"] == 50
    assert run_data["risk_analysis"] is not None


@pytest.mark.asyncio
async def test_audit_logs_endpoint(client: AsyncClient, ensure_merchant):
    """GET /api/v1/audit/logs returns ledger items."""
    audit_res = await client.get(f"/api/v1/audit/logs?merchant_id={TEST_MERCHANT_ID}")
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert isinstance(logs, list)
    if len(logs) > 0:
        assert "cryptographicHash" in logs[0]
        assert "actorType" in logs[0]
