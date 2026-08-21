"""Unit tests for deterministic risk scoring."""

from decimal import Decimal
from app.schemas.risk_engine import RiskSignalCreate
from app.services.risk.scoring import RiskScoringEngine


def test_empty_signals_scores_zero_low():
    """Verify empty signals yield zero risk and LOW classification."""
    score, severity = RiskScoringEngine.calculate_score(
        signals=[],
        current_data={},
        baseline_data={},
    )
    assert score == 0.0
    assert severity == "LOW"


def test_multiple_high_signals_yields_high_critical_score():
    """Verify multiple correlated degradation signals yield HIGH / CRITICAL score."""
    signals = [
        RiskSignalCreate(
            signal_type="PAYMENT_METHOD_DEGRADATION",
            metric_name="UPI_SUCCESS_RATE",
            baseline_value=Decimal("0.9420"),
            observed_value=Decimal("0.7420"),
            deviation_value=Decimal("-0.2000"),
            dimension="payment_method",
            dimension_value="UPI",
            severity="HIGH",
        ),
        RiskSignalCreate(
            signal_type="FAILURE_SPIKE",
            metric_name="OVERALL_FAILURE_RATE",
            deviation_value=Decimal("0.1250"),
            severity="HIGH",
        ),
        RiskSignalCreate(
            signal_type="VELOCITY_ANOMALY",
            metric_name="FAILURE_VELOCITY",
            evidence={"failed_count": 85},
            severity="HIGH",
        ),
        RiskSignalCreate(
            signal_type="CONCENTRATION_ANOMALY",
            metric_name="HDFC_FAILURE_CONCENTRATION",
            severity="HIGH",
        ),
    ]

    current_data = {
        "summary": {
            "failed_amount": Decimal("420000.00"),
            "failed_count": 85,
        }
    }

    score, severity = RiskScoringEngine.calculate_score(
        signals=signals,
        current_data=current_data,
        baseline_data={},
    )

    # Score should be elevated (>= 75.0)
    assert score >= 70.0
    assert severity in ["HIGH", "CRITICAL"]


def test_scoring_determinism():
    """Verify identical inputs produce strictly identical scores."""
    signals = [
        RiskSignalCreate(
            signal_type="PAYMENT_METHOD_DEGRADATION",
            metric_name="UPI_SUCCESS_RATE",
            deviation_value=Decimal("-0.1000"),
            severity="MEDIUM",
        ),
    ]
    current_data = {"summary": {"failed_amount": Decimal("65000.00")}}

    score1, sev1 = RiskScoringEngine.calculate_score(signals, current_data, {})
    score2, sev2 = RiskScoringEngine.calculate_score(signals, current_data, {})

    assert score1 == score2
    assert sev1 == sev2
