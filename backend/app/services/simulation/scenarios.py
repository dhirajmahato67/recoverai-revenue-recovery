"""Scenario configuration and definitions for synthetic transaction generation."""

from decimal import Decimal
from typing import Dict
from app.schemas.simulation import ScenarioConfig, ScenarioInfo, ScenarioType

# Catalog of standardized Buildathon demonstration scenarios
SCENARIO_DEFINITIONS: Dict[ScenarioType, ScenarioConfig] = {
    "NORMAL_BASELINE": ScenarioConfig(
        scenario_id="NORMAL_BASELINE",
        name="Normal Baseline Operations",
        description="Steady-state payment operations across all payment methods and partner banks with healthy conversion rates (~94.2%).",
        target_success_rate=0.942,
        method_success_rates={
            "UPI": 0.942,
            "CARD": 0.955,
            "NETBANKING": 0.950,
            "WALLET": 0.960,
        },
        bank_success_rates={
            "HDFC": 0.945,
            "ICICI": 0.940,
            "SBI": 0.938,
            "AXIS": 0.942,
            "KOTAK": 0.948,
            "OTHER": 0.940,
        },
        primary_failure_error_code="BANK_DECLINED",
        primary_failure_reason="Transaction declined by customer bank due to standard customer limits or incorrect credentials.",
    ),
    "UPI_DEGRADATION": ScenarioConfig(
        scenario_id="UPI_DEGRADATION",
        name="UPI Payment Degradation",
        description="Significant drop in UPI conversions driven by upstream issuer timeout degradation (specifically HDFC UPI falling to ~68.9%), while Card and NetBanking remain healthy.",
        target_success_rate=0.817,
        method_success_rates={
            "UPI": 0.742,
            "CARD": 0.955,
            "NETBANKING": 0.950,
            "WALLET": 0.960,
        },
        bank_success_rates={
            "HDFC": 0.689,
            "ICICI": 0.920,
            "SBI": 0.915,
            "AXIS": 0.925,
            "KOTAK": 0.930,
            "OTHER": 0.920,
        },
        primary_failure_error_code="GATEWAY_TIMEOUT",
        primary_failure_reason="Issuer bank timeout on UPI response (p95 latency > 8000ms).",
    ),
    "RECOVERY_AUTO_STOP": ScenarioConfig(
        scenario_id="RECOVERY_AUTO_STOP",
        name="Recovery Auto-Stop (Circuit Breaker)",
        description="Degraded batch recovery simulation where retry failure threshold exceeds safety policy (>30%), demonstrating automated circuit breaker protection.",
        target_success_rate=0.620,
        method_success_rates={
            "UPI": 0.580,
            "CARD": 0.700,
            "NETBANKING": 0.650,
            "WALLET": 0.800,
        },
        bank_success_rates={
            "HDFC": 0.520,
            "ICICI": 0.680,
            "SBI": 0.610,
            "AXIS": 0.650,
            "KOTAK": 0.700,
            "OTHER": 0.600,
        },
        primary_failure_error_code="RETRY_EXHAUSTED",
        primary_failure_reason="Downstream gateway unavailable during automated recovery dispatch.",
    ),
    "CHECKOUT_DROPOFF": ScenarioConfig(
        scenario_id="CHECKOUT_DROPOFF",
        name="Checkout Abandonment & Authorization Failure",
        description="Spike in 3DS OTP authorization dropouts affecting credit and debit card checkouts.",
        target_success_rate=0.760,
        method_success_rates={
            "UPI": 0.940,
            "CARD": 0.520,
            "NETBANKING": 0.880,
            "WALLET": 0.950,
        },
        bank_success_rates={
            "HDFC": 0.750,
            "ICICI": 0.740,
            "SBI": 0.720,
            "AXIS": 0.770,
            "KOTAK": 0.760,
            "OTHER": 0.750,
        },
        primary_failure_error_code="OTP_TIMEOUT",
        primary_failure_reason="Customer failed to enter 3D Secure OTP within the authentication timeout.",
    ),
    "SUBSCRIPTION_FAILURES": ScenarioConfig(
        scenario_id="SUBSCRIPTION_FAILURES",
        name="Subscription Mandate Failures",
        description="E-mandate debit presentation failure spike on recurring auto-debit billing cycles.",
        target_success_rate=0.710,
        method_success_rates={
            "UPI": 0.690,
            "CARD": 0.720,
            "NETBANKING": 0.700,
            "WALLET": 0.850,
        },
        bank_success_rates={
            "HDFC": 0.710,
            "ICICI": 0.700,
            "SBI": 0.680,
            "AXIS": 0.720,
            "KOTAK": 0.740,
            "OTHER": 0.700,
        },
        primary_failure_error_code="MANDATE_EXECUTION_FAILED",
        primary_failure_reason="Standing instruction mandate execution failed due to issuer system rejection.",
    ),
    "GATEWAY_LATENCY": ScenarioConfig(
        scenario_id="GATEWAY_LATENCY",
        name="Gateway Latency Spike",
        description="High connection latency resulting in HTTP 504 and gateway timeout errors across multiple aggregators.",
        target_success_rate=0.830,
        method_success_rates={
            "UPI": 0.820,
            "CARD": 0.840,
            "NETBANKING": 0.810,
            "WALLET": 0.880,
        },
        bank_success_rates={
            "HDFC": 0.820,
            "ICICI": 0.830,
            "SBI": 0.800,
            "AXIS": 0.840,
            "KOTAK": 0.850,
            "OTHER": 0.820,
        },
        primary_failure_error_code="GATEWAY_TIMEOUT",
        primary_failure_reason="Aggregator gateway response timeout exceeded 10000ms threshold.",
    ),
}

SCENARIO_METADATA: Dict[ScenarioType, ScenarioInfo] = {
    "NORMAL_BASELINE": ScenarioInfo(
        id="NORMAL_BASELINE",
        name="Normal Baseline Operations",
        badge="Healthy",
        description="Standard operating baseline with 94.2% overall payment conversion and distributed method mix.",
        target_success_rate=0.942,
        primary_risk_title="All Systems Operational",
        revenue_at_risk_estimate_inr=Decimal("0.00"),
        recoverable_revenue_estimate_inr=Decimal("0.00"),
    ),
    "UPI_DEGRADATION": ScenarioInfo(
        id="UPI_DEGRADATION",
        name="UPI Payment Degradation",
        badge="Critical Incident",
        description="Primary Buildathon demonstration: UPI success rate drops to 81.7% with HDFC UPI falling to 68.9%. ₹8.40L revenue at risk.",
        target_success_rate=0.817,
        primary_risk_title="UPI Payment Degradation",
        revenue_at_risk_estimate_inr=Decimal("840000.00"),
        recoverable_revenue_estimate_inr=Decimal("210000.00"),
    ),
    "RECOVERY_AUTO_STOP": ScenarioInfo(
        id="RECOVERY_AUTO_STOP",
        name="Recovery Auto-Stop",
        badge="Circuit Breaker",
        description="Auto-recovery execution encounters elevated retry failure (>30%) and triggers automated stop rule.",
        target_success_rate=0.620,
        primary_risk_title="Circuit Breaker Protection",
        revenue_at_risk_estimate_inr=Decimal("520000.00"),
        recoverable_revenue_estimate_inr=Decimal("130000.00"),
    ),
    "CHECKOUT_DROPOFF": ScenarioInfo(
        id="CHECKOUT_DROPOFF",
        name="Checkout Drop-off",
        badge="3DS Drop",
        description="Credit and Debit card OTP authentication dropouts causing elevated checkout abandonment.",
        target_success_rate=0.760,
        primary_risk_title="Card 3DS Authorization Drop",
        revenue_at_risk_estimate_inr=Decimal("380000.00"),
        recoverable_revenue_estimate_inr=Decimal("95000.00"),
    ),
    "SUBSCRIPTION_FAILURES": ScenarioInfo(
        id="SUBSCRIPTION_FAILURES",
        name="Subscription Failures",
        badge="Mandate Spike",
        description="Recurring mandate auto-debits failing across multiple issuer banking portals.",
        target_success_rate=0.710,
        primary_risk_title="Recurring Mandate Rejections",
        revenue_at_risk_estimate_inr=Decimal("460000.00"),
        recoverable_revenue_estimate_inr=Decimal("115000.00"),
    ),
    "GATEWAY_LATENCY": ScenarioInfo(
        id="GATEWAY_LATENCY",
        name="Gateway Latency",
        badge="High Latency",
        description="High p95/p99 latency spikes resulting in connection timeouts across payment aggregators.",
        target_success_rate=0.830,
        primary_risk_title="Aggregator Timeout Degradation",
        revenue_at_risk_estimate_inr=Decimal("290000.00"),
        recoverable_revenue_estimate_inr=Decimal("72000.00"),
    ),
}


class ScenarioRegistry:
    """Registry providing scenario retrieval and configuration matching."""

    @classmethod
    def get_scenario(cls, scenario_id: ScenarioType) -> ScenarioConfig:
        """Retrieve the configuration for a given scenario ID."""
        if scenario_id not in SCENARIO_DEFINITIONS:
            return SCENARIO_DEFINITIONS["NORMAL_BASELINE"]
        return SCENARIO_DEFINITIONS[scenario_id]

    @classmethod
    def list_scenarios(cls) -> list[ScenarioInfo]:
        """List all available scenario metadata definitions."""
        return list(SCENARIO_METADATA.values())
