"""Unit tests for the Synthetic Transaction Generator."""

import uuid
from decimal import Decimal
from app.services.simulation.generator import SyntheticTransactionGenerator
from app.services.simulation.scenarios import ScenarioRegistry


def test_deterministic_generation_same_seed():
    """Verify that same seed produces identical synthetic transactions."""
    gen1 = SyntheticTransactionGenerator(seed=42)
    gen2 = SyntheticTransactionGenerator(seed=42)

    batch1 = gen1.generate_batch(count=50, scenario_id="NORMAL_BASELINE")
    batch2 = gen2.generate_batch(count=50, scenario_id="NORMAL_BASELINE")

    assert len(batch1) == 50
    assert len(batch2) == 50

    for tx1, tx2 in zip(batch1, batch2):
        assert tx1.external_payment_id == tx2.external_payment_id
        assert tx1.amount == tx2.amount
        assert tx1.payment_method == tx2.payment_method
        assert tx1.bank == tx2.bank
        assert tx1.status == tx2.status
        assert tx1.error_code == tx2.error_code


def test_different_seeds_produce_different_streams():
    """Verify that different seeds produce distinct synthetic transactions."""
    gen1 = SyntheticTransactionGenerator(seed=42)
    gen2 = SyntheticTransactionGenerator(seed=99)

    batch1 = gen1.generate_batch(count=20, scenario_id="NORMAL_BASELINE")
    batch2 = gen2.generate_batch(count=20, scenario_id="NORMAL_BASELINE")

    # IDs include seed
    assert batch1[0].external_payment_id != batch2[0].external_payment_id


def test_payment_method_distribution():
    """Verify generated payment methods roughly match configured distributions over large batch."""
    gen = SyntheticTransactionGenerator(seed=123)
    batch = gen.generate_batch(count=1000, scenario_id="NORMAL_BASELINE")

    method_counts = {}
    for tx in batch:
        method_counts[tx.payment_method] = method_counts.get(tx.payment_method, 0) + 1

    # UPI should be the dominant method (~60%)
    assert method_counts["UPI"] > 500
    # CARD should be second (~20%)
    assert method_counts["CARD"] > 100
    # NETBANKING (~12%) and WALLET (~8%)
    assert method_counts["NETBANKING"] > 50
    assert method_counts["WALLET"] > 30


def test_upi_degradation_scenario_failures():
    """Verify UPI degradation scenario produces significantly higher failure rate for HDFC UPI."""
    gen = SyntheticTransactionGenerator(seed=42)
    batch = gen.generate_batch(count=1000, scenario_id="UPI_DEGRADATION")

    hdfc_upi_total = 0
    hdfc_upi_failed = 0
    card_total = 0
    card_failed = 0

    for tx in batch:
        if tx.payment_method == "UPI" and tx.bank == "HDFC":
            hdfc_upi_total += 1
            if tx.status == "FAILED":
                hdfc_upi_failed += 1
                assert tx.error_code in ["GATEWAY_TIMEOUT", "BANK_DECLINED"]
        elif tx.payment_method == "CARD":
            card_total += 1
            if tx.status == "FAILED":
                card_failed += 1

    assert hdfc_upi_total > 150
    hdfc_upi_fail_rate = hdfc_upi_failed / hdfc_upi_total
    # HDFC UPI failure rate should be elevated (~30%)
    assert hdfc_upi_fail_rate > 0.20

    if card_total > 0:
        card_fail_rate = card_failed / card_total
        # Card failure rate should remain low (~4-6%)
        assert card_fail_rate < 0.15


def test_generator_stream_chunking():
    """Verify generator stream yields chunks properly without loading entire dataset."""
    gen = SyntheticTransactionGenerator(seed=7)
    chunks = list(gen.generate_stream(count=2500, chunk_size=500, scenario_id="NORMAL_BASELINE"))

    assert len(chunks) == 5
    for chunk in chunks:
        assert len(chunk) == 500

    total_count = sum(len(c) for c in chunks)
    assert total_count == 2500


def test_financial_amounts_valid():
    """Verify all synthesized amounts are positive Decimal instances with 2 decimal places."""
    gen = SyntheticTransactionGenerator(seed=10)
    batch = gen.generate_batch(count=100)

    for tx in batch:
        assert isinstance(tx.amount, Decimal)
        assert tx.amount > Decimal("0.00")
        assert tx.currency == "INR"
