"""Integration tests for Phase 5 Investigation FastAPI endpoints."""

import datetime
import uuid
import pytest
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Merchant, RiskCase
from app.services.ingestion.ingestor import TransactionIngestionService
from app.services.simulation.generator import SyntheticTransactionGenerator

TEST_MERCHANT_ID = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
async def setup_api_case(db_session: AsyncSession) -> RiskCase:
    """Fixture ensuring merchant, payments, and risk case exist."""
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

    gen = SyntheticTransactionGenerator(seed=501, merchant_id=uid)
    batch = gen.generate_batch(count=60, scenario_id="UPI_DEGRADATION")
    await ingestor.ingest_batch(merchant_id=uid, transactions=batch)

    case = RiskCase(
        id=uuid.uuid4(),
        merchant_id=uid,
        case_reference="RC-API-01",
        risk_type="PAYMENT_DEGRADATION",
        severity="HIGH",
        status="OPEN",
        title="UPI Payment Degradation",
        summary="Automated telemetry detected drop in UPI conversions",
        revenue_at_risk=Decimal("150000.00"),
        estimated_recoverable_revenue=Decimal("37500.00"),
        confidence_score=Decimal("0.9000"),
        detected_at=now,
    )
    db_session.add(case)
    await db_session.commit()
    return case


@pytest.mark.asyncio
async def test_post_and_get_investigations_endpoints(client: AsyncClient, setup_api_case: RiskCase):
    """Test POST /api/v1/investigations and GET /api/v1/investigations/{id}."""
    case = setup_api_case

    # 1. Create investigation
    post_res = await client.post(
        "/api/v1/investigations",
        json={"risk_case_id": case.case_reference, "merchant_id": TEST_MERCHANT_ID},
    )
    assert post_res.status_code == 200
    inv_data = post_res.json()
    assert inv_data["caseId"] == case.case_reference
    assert inv_data["status"] == "COMPLETED"
    assert "finding" in inv_data
    assert len(inv_data["steps"]) >= 4
    assert len(inv_data["toolExecutions"]) >= 3
    inv_id = inv_data["id"]

    # 2. Get details
    get_res = await client.get(f"/api/v1/investigations/{inv_id}?merchant_id={TEST_MERCHANT_ID}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == inv_id

    # 3. Get evidence
    ev_res = await client.get(f"/api/v1/investigations/{inv_id}/evidence?merchant_id={TEST_MERCHANT_ID}")
    assert ev_res.status_code == 200
    assert isinstance(ev_res.json(), list)

    # 4. Get timeline
    time_res = await client.get(f"/api/v1/investigations/{inv_id}/timeline?merchant_id={TEST_MERCHANT_ID}")
    assert time_res.status_code == 200
    assert len(time_res.json()) >= 3

    # 5. Get root cause candidates
    rc_res = await client.get(f"/api/v1/investigations/{inv_id}/root-cause?merchant_id={TEST_MERCHANT_ID}")
    assert rc_res.status_code == 200
    assert len(rc_res.json()) >= 2

    # 6. List investigations
    list_res = await client.get(f"/api/v1/investigations?merchant_id={TEST_MERCHANT_ID}")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1
