"""Deterministic Synthetic Transaction Generator for RecoverAI."""

import datetime
import random
import uuid
from decimal import Decimal
from typing import Generator, List, Sequence
from app.schemas.simulation import (
    BankType,
    PaymentMethodType,
    ScenarioType,
    SyntheticTransactionItem,
)
from app.services.simulation.scenarios import ScenarioRegistry

# Standard synthetic customer pool matching Phase 3 seed
DEFAULT_CUSTOMER_POOL = [
    ("cust_acme_0001", "Aarav Sharma", "aarav.sharma@example.local", "9182"),
    ("cust_acme_0002", "Priya Mehta", "priya.mehta@example.local", "8271"),
    ("cust_acme_0003", "Rahul Verma", "rahul.verma@example.local", "7362"),
    ("cust_acme_0004", "Ananya Singh", "ananya.singh@example.local", "6453"),
    ("cust_acme_0005", "Rohan Gupta", "rohan.gupta@example.local", "5544"),
    ("cust_acme_0006", "Neha Patel", "neha.patel@example.local", "4635"),
    ("cust_acme_0007", "Aditya Rao", "aditya.rao@example.local", "3726"),
    ("cust_acme_0008", "Sneha Iyer", "sneha.iyer@example.local", "2817"),
    ("cust_acme_0009", "Kabir Joshi", "kabir.joshi@example.local", "1908"),
    ("cust_acme_0010", "Pooja Nair", "pooja.nair@example.local", "9019"),
    ("cust_acme_0011", "Vikram Malhotra", "vikram.malhotra@example.local", "8120"),
    ("cust_acme_0012", "Ishita Roy", "ishita.roy@example.local", "7231"),
    ("cust_acme_0013", "Arjun Kapoor", "arjun.kapoor@example.local", "6342"),
    ("cust_acme_0014", "Kavya Pillai", "kavya.pillai@example.local", "5453"),
    ("cust_acme_0015", "Varun Deshmukh", "varun.deshmukh@example.local", "4564"),
    ("cust_acme_0016", "Divya Menon", "divya.menon@example.local", "3675"),
    ("cust_acme_0017", "Sameer Saxena", "sameer.saxena@example.local", "2786"),
    ("cust_acme_0018", "Tanvi Kulkarni", "tanvi.kulkarni@example.local", "1897"),
    ("cust_acme_0019", "Manoj Choudhary", "manoj.choudhary@example.local", "9908"),
    ("cust_acme_0020", "Ritu Banerjee", "ritu.banerjee@example.local", "8819"),
    ("cust_acme_0021", "Deepak Bhatt", "deepak.bhatt@example.local", "7720"),
    ("cust_acme_0022", "Swati Sengupta", "swati.sengupta@example.local", "6631"),
    ("cust_acme_0023", "Nitin Agarwal", "nitin.agarwal@example.local", "5542"),
    ("cust_acme_0024", "Meera Nambiar", "meera.nambiar@example.local", "4453"),
    ("cust_acme_0025", "Siddharth Ghosh", "siddharth.ghosh@example.local", "3364"),
]

# Standard retail transaction amounts
STANDARD_AMOUNTS: List[Decimal] = [
    Decimal("499.00"),
    Decimal("999.00"),
    Decimal("1499.00"),
    Decimal("2450.00"),
    Decimal("3200.00"),
    Decimal("4800.00"),
    Decimal("7500.00"),
    Decimal("12500.00"),
    Decimal("18900.00"),
    Decimal("24999.00"),
]

# Configurable method distribution (100% total): 60% UPI, 20% CARD, 12% NETBANKING, 8% WALLET
DEFAULT_METHOD_DISTRIBUTION: List[PaymentMethodType] = (
    ["UPI"] * 60 + ["CARD"] * 20 + ["NETBANKING"] * 12 + ["WALLET"] * 8
)

# Configurable bank distribution (100% total): 40% HDFC, 25% ICICI, 20% SBI, 15% AXIS
DEFAULT_BANK_DISTRIBUTION: List[BankType] = (
    ["HDFC"] * 40 + ["ICICI"] * 25 + ["SBI"] * 20 + ["AXIS"] * 15
)


class SyntheticTransactionGenerator:
    """Deterministic, high-throughput generator for synthetic payment transaction streams."""

    def __init__(
        self,
        seed: int = 42,
        merchant_id: uuid.UUID | None = None,
        method_distribution: Sequence[PaymentMethodType] | None = None,
        bank_distribution: Sequence[BankType] | None = None,
        amounts: Sequence[Decimal] | None = None,
        customer_pool: Sequence[tuple[str, str, str, str]] | None = None,
    ) -> None:
        self.seed = seed
        self.prng = random.Random(seed)
        self.merchant_id = merchant_id or uuid.UUID("00000000-0000-0000-0000-000000000001")
        self.methods = list(method_distribution or DEFAULT_METHOD_DISTRIBUTION)
        self.banks = list(bank_distribution or DEFAULT_BANK_DISTRIBUTION)
        self.amounts = list(amounts or STANDARD_AMOUNTS)
        self.customers = list(customer_pool or DEFAULT_CUSTOMER_POOL)

    def reseed(self, seed: int) -> None:
        """Reset the PRNG instance with a new seed for determinism."""
        self.seed = seed
        self.prng = random.Random(seed)

    def generate_single_transaction(
        self,
        scenario_id: ScenarioType = "NORMAL_BASELINE",
        index: int = 1,
        timestamp: datetime.datetime | None = None,
    ) -> SyntheticTransactionItem:
        """Synthesize a single deterministic transaction according to the specified scenario."""
        scenario = ScenarioRegistry.get_scenario(scenario_id)
        ts = timestamp or datetime.datetime.now(datetime.timezone.utc)

        # Select dimensions
        cust_ext_id, cust_name, cust_email, cust_phone = self.prng.choice(self.customers)
        method = self.prng.choice(self.methods)
        bank = self.prng.choice(self.banks)
        amount = self.prng.choice(self.amounts)

        # External identifiers
        ext_order_id = f"ord_synth_{self.seed}_{index:06d}"
        ext_payment_id = f"pay_synth_{self.seed}_{index:06d}"
        event_id = f"evt_synth_{self.seed}_{index:06d}"

        # Determine success / failure probability
        # Specific scenario handling for correlated failures
        if scenario_id == "UPI_DEGRADATION":
            if method == "UPI" and bank == "HDFC":
                # HDFC UPI has high failure rate (~31.1% fail -> 68.9% success)
                is_failed = self.prng.random() >= scenario.bank_success_rates.get("HDFC", 0.689)
            elif method == "UPI":
                is_failed = self.prng.random() >= scenario.method_success_rates.get("UPI", 0.742)
            else:
                method_rate = scenario.method_success_rates.get(method, 0.95)
                is_failed = self.prng.random() >= method_rate
        else:
            # General scenario success rate combination
            method_rate = scenario.method_success_rates.get(method, scenario.target_success_rate)
            bank_rate = scenario.bank_success_rates.get(bank, scenario.target_success_rate)
            combined_success_rate = (method_rate + bank_rate) / 2.0
            is_failed = self.prng.random() >= combined_success_rate

        status = "FAILED" if is_failed else "CAPTURED"
        captured_at = ts if status == "CAPTURED" else None

        # Determine error codes
        error_code = None
        error_reason = None
        if is_failed:
            if scenario_id == "UPI_DEGRADATION" and method == "UPI":
                # 75% timeouts for HDFC UPI, 25% bank declines
                if bank == "HDFC" and self.prng.random() < 0.75:
                    error_code = "GATEWAY_TIMEOUT"
                    error_reason = "Issuer bank timeout on UPI response (p95 latency > 8000ms)"
                else:
                    error_code = "BANK_DECLINED"
                    error_reason = "Transaction declined by issuing bank"
            elif scenario.primary_failure_error_code and self.prng.random() < 0.70:
                error_code = scenario.primary_failure_error_code
                error_reason = scenario.primary_failure_reason or "Automated scenario failure"
            else:
                error_code = self.prng.choice(["BANK_DECLINED", "INSUFFICIENT_FUNDS", "UPI_PIN_EXPIRED", "NETWORK_ERROR"])
                error_reason = f"Payment failure: {error_code.replace('_', ' ').title()}"

        event_type = "payment.captured" if status == "CAPTURED" else "payment.failed"

        return SyntheticTransactionItem(
            external_order_id=ext_order_id,
            external_payment_id=ext_payment_id,
            external_customer_id=cust_ext_id,
            customer_name=cust_name,
            customer_email=cust_email,
            customer_phone=cust_phone,
            amount=amount,
            currency="INR",
            status=status,
            payment_method=method,
            bank=bank,
            error_code=error_code,
            error_reason=error_reason,
            created_at=ts,
            captured_at=captured_at,
            event_id=event_id,
            event_type=event_type,
        )

    def generate_batch(
        self,
        count: int = 100,
        scenario_id: ScenarioType = "NORMAL_BASELINE",
        start_time: datetime.datetime | None = None,
        end_time: datetime.datetime | None = None,
    ) -> List[SyntheticTransactionItem]:
        """Generate a complete batch of synthetic transactions."""
        now = datetime.datetime.now(datetime.timezone.utc)
        end = end_time or now
        start = start_time or (end - datetime.timedelta(hours=2))

        duration_seconds = max(1.0, (end - start).total_seconds())
        step_seconds = duration_seconds / max(1, count)

        items: List[SyntheticTransactionItem] = []
        for i in range(1, count + 1):
            ts = start + datetime.timedelta(seconds=step_seconds * (i - 1))
            item = self.generate_single_transaction(scenario_id=scenario_id, index=i, timestamp=ts)
            items.append(item)
        return items

    def generate_stream(
        self,
        count: int = 10000,
        scenario_id: ScenarioType = "NORMAL_BASELINE",
        chunk_size: int = 500,
        start_time: datetime.datetime | None = None,
        end_time: datetime.datetime | None = None,
    ) -> Generator[List[SyntheticTransactionItem], None, None]:
        """Stream chunks of synthetic transactions for memory-efficient large-scale generation (10,000+)."""
        now = datetime.datetime.now(datetime.timezone.utc)
        end = end_time or now
        start = start_time or (end - datetime.timedelta(hours=2))

        duration_seconds = max(1.0, (end - start).total_seconds())
        step_seconds = duration_seconds / max(1, count)

        chunk: List[SyntheticTransactionItem] = []
        for i in range(1, count + 1):
            ts = start + datetime.timedelta(seconds=step_seconds * (i - 1))
            item = self.generate_single_transaction(scenario_id=scenario_id, index=i, timestamp=ts)
            chunk.append(item)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk
