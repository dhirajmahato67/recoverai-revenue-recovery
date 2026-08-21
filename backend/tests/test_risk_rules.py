"""Unit tests for modular risk detection rules."""

from decimal import Decimal
from app.services.risk.rules import (
    PaymentMethodDegradationRule,
    FailureSpikeRule,
    VelocityAnomalyRule,
    RevenueAtRiskRule,
    ConcentrationAnomalyRule,
    ErrorCodeSpikeRule,
)


def test_payment_method_degradation_rule_detects_drop():
    """Verify Rule 1 detects when a payment method success rate drops by more than threshold."""
    rule = PaymentMethodDegradationRule(drop_threshold=0.05)

    current_data = {
        "methods": {
            "UPI": {"total_count": 100, "captured_count": 75, "failed_count": 25, "success_rate": 0.75},
            "CARD": {"total_count": 50, "captured_count": 48, "failed_count": 2, "success_rate": 0.96},
        }
    }
    baseline_data = {
        "methods": {
            "UPI": {"total_count": 1000, "captured_count": 942, "failed_count": 58, "success_rate": 0.942},
            "CARD": {"total_count": 500, "captured_count": 478, "failed_count": 22, "success_rate": 0.956},
        }
    }

    signals = rule.evaluate(current_data, baseline_data)
    assert len(signals) == 1
    sig = signals[0]
    assert sig.signal_type == "PAYMENT_METHOD_DEGRADATION"
    assert sig.dimension_value == "UPI"
    assert sig.severity in ["HIGH", "CRITICAL"]
    assert sig.observed_value == Decimal("0.7500")


def test_payment_method_degradation_rule_ignores_healthy_stream():
    """Verify Rule 1 does not generate false alerts when methods are healthy."""
    rule = PaymentMethodDegradationRule(drop_threshold=0.05)

    current_data = {
        "methods": {
            "UPI": {"total_count": 100, "captured_count": 94, "failed_count": 6, "success_rate": 0.94},
            "CARD": {"total_count": 50, "captured_count": 48, "failed_count": 2, "success_rate": 0.96},
        }
    }
    baseline_data = {
        "methods": {
            "UPI": {"total_count": 1000, "captured_count": 942, "failed_count": 58, "success_rate": 0.942},
            "CARD": {"total_count": 500, "captured_count": 478, "failed_count": 22, "success_rate": 0.956},
        }
    }

    signals = rule.evaluate(current_data, baseline_data)
    assert len(signals) == 0


def test_failure_spike_rule():
    """Verify Rule 2 detects overall checkout failure surges."""
    rule = FailureSpikeRule(spike_threshold=0.08)

    current_data = {
        "summary": {"total_count": 200, "captured_count": 160, "failed_count": 40, "success_rate": 0.80}
    }
    baseline_data = {
        "summary": {"total_count": 2000, "captured_count": 1900, "failed_count": 100, "success_rate": 0.95}
    }

    signals = rule.evaluate(current_data, baseline_data)
    assert len(signals) == 1
    assert signals[0].signal_type == "FAILURE_SPIKE"
    assert signals[0].severity in ["HIGH", "MEDIUM", "CRITICAL"]


def test_velocity_anomaly_rule():
    """Verify Rule 3 flags failure bursts above threshold."""
    rule = VelocityAnomalyRule(failure_velocity_threshold=40)

    current_data = {"summary": {"failed_count": 65}, "window_minutes": 120}
    baseline_data = {}

    signals = rule.evaluate(current_data, baseline_data)
    assert len(signals) == 1
    assert signals[0].signal_type == "VELOCITY_ANOMALY"


def test_revenue_at_risk_rule():
    """Verify Rule 4 flags uncollected revenue volumes exceeding threshold."""
    rule = RevenueAtRiskRule(threshold_inr=Decimal("50000.00"))

    current_data = {"summary": {"failed_amount": Decimal("184500.00")}}
    baseline_data = {}

    signals = rule.evaluate(current_data, baseline_data)
    assert len(signals) == 1
    assert signals[0].signal_type == "REVENUE_AT_RISK"
    assert signals[0].severity == "HIGH"


def test_concentration_anomaly_rule():
    """Verify Rule 5 detects when failures disproportionately concentrate in one bank."""
    rule = ConcentrationAnomalyRule(concentration_threshold=0.40)

    current_data = {
        "summary": {"failed_count": 50},
        "banks": {
            "HDFC": {"failed_count": 35, "total_count": 60, "success_rate": 0.416},
            "ICICI": {"failed_count": 10, "total_count": 40, "success_rate": 0.75},
            "SBI": {"failed_count": 5, "total_count": 30, "success_rate": 0.833},
        },
    }
    baseline_data = {}

    signals = rule.evaluate(current_data, baseline_data)
    assert len(signals) == 1
    assert signals[0].signal_type == "CONCENTRATION_ANOMALY"
    assert signals[0].dimension_value == "HDFC"


def test_error_code_spike_rule():
    """Verify Rule 6 detects dominant error codes like GATEWAY_TIMEOUT."""
    rule = ErrorCodeSpikeRule(error_share_threshold=0.30)

    current_data = {
        "summary": {"failed_count": 40},
        "errors": {
            "GATEWAY_TIMEOUT": 28,  # 70% share (> 30%)
            "BANK_DECLINED": 8,     # 20% share (< 30%)
            "OTHER": 4,             # 10% share (< 30%)
        },
    }
    baseline_data = {}

    signals = rule.evaluate(current_data, baseline_data)
    assert len(signals) == 1
    assert signals[0].signal_type == "ERROR_CODE_SPIKE"
    assert signals[0].dimension_value == "GATEWAY_TIMEOUT"
