"""Performance and scale benchmark tests for 10,000 synthetic transactions."""

import time
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Merchant
from app.services.ingestion.ingestor import TransactionIngestionService
from app.services.simulation.generator import SyntheticTransactionGenerator

TEST_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
async def ensure_merchant(db_session: AsyncSession):
    """Seed test merchant."""
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


def test_generator_performance_10000_transactions():
    """Benchmark: Synthesizing 10,000 transactions in-memory must complete in < 1.0 second."""
    gen = SyntheticTransactionGenerator(seed=999)

    t0 = time.perf_counter()
    batch = gen.generate_batch(count=10000, scenario_id="UPI_DEGRADATION")
    t1 = time.perf_counter()

    gen_duration = t1 - t0
    rate = len(batch) / gen_duration

    assert len(batch) == 10000
    assert gen_duration < 1.0, f"Generation of 10,000 transactions took {gen_duration:.3f}s (exceeds 1.0s limit)"
    print(f"\n[BENCHMARK] Generated 10,000 transactions in {gen_duration:.3f}s ({rate:,.0f} tx/sec)")


@pytest.mark.asyncio
async def test_chunked_ingestion_performance(db_session: AsyncSession, ensure_merchant):
    """Benchmark: Ingestion of 1,000 transactions via chunked batching."""
    service = TransactionIngestionService(db_session)
    gen = SyntheticTransactionGenerator(seed=888, merchant_id=TEST_MERCHANT_ID)

    t0 = time.perf_counter()
    batch = gen.generate_batch(count=1000, scenario_id="NORMAL_BASELINE")
    t1 = time.perf_counter()

    ingest_res = await service.ingest_batch(
        merchant_id=TEST_MERCHANT_ID,
        transactions=batch,
        chunk_size=500,
    )
    t2 = time.perf_counter()

    ingest_duration = t2 - t1
    total_duration = t2 - t0
    throughput = len(batch) / ingest_duration

    assert ingest_res.accepted == 1000
    assert ingest_res.rejected == 0
    print(
        f"\n[BENCHMARK] Ingested 1,000 transactions in {ingest_duration:.3f}s "
        f"({throughput:,.0f} tx/sec, Total time: {total_duration:.3f}s)"
    )
