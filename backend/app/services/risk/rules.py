"""Modular Risk Detection Rules for RecoverAI."""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any
from app.schemas.risk_engine import RiskSeverity, RiskSignalCreate


class DetectionRule(ABC):
    """Abstract base class for all independent, testable risk detection rules."""

    def __init__(self, rule_id: str, name: str, description: str) -> None:
        self.rule_id = rule_id
        self.name = name
        self.description = description

    @abstractmethod
    def evaluate(self, current_data: dict[str, Any], baseline_data: dict[str, Any]) -> list[RiskSignalCreate]:
        """Evaluate detection rule against current and baseline operational datasets."""
        pass


class PaymentMethodDegradationRule(DetectionRule):
    """Rule 1: Detects significant decline in individual payment method conversion rates."""

    def __init__(self, drop_threshold: float = 0.05) -> None:
        super().__init__(
            rule_id="RULE_001_METHOD_DEGRADATION",
            name="Payment Method Degradation",
            description="Identifies statistically significant drops in payment method success rate compared to historical baseline.",
        )
        self.drop_threshold = drop_threshold

    def evaluate(self, current_data: dict[str, Any], baseline_data: dict[str, Any]) -> list[RiskSignalCreate]:
        signals: list[RiskSignalCreate] = []
        curr_methods = current_data.get("methods", {})
        base_methods = baseline_data.get("methods", {})

        for method, curr_stat in curr_methods.items():
            curr_rate = curr_stat.get("success_rate", 1.0)
            base_stat = base_methods.get(method, {})
            base_rate = base_stat.get("success_rate", 0.95)

            delta = curr_rate - base_rate  # Negative delta indicates degradation
            if delta <= -self.drop_threshold and curr_stat.get("total_count", 0) >= 5:
                abs_drop = abs(delta)
                severity: RiskSeverity = "CRITICAL" if abs_drop >= 0.20 else ("HIGH" if abs_drop >= 0.10 else "MEDIUM")
                confidence = min(0.98, 0.80 + (curr_stat.get("total_count", 0) / 500.0) * 0.18)

                signals.append(
                    RiskSignalCreate(
                        signal_type="PAYMENT_METHOD_DEGRADATION",
                        metric_name=f"{method}_SUCCESS_RATE",
                        baseline_value=Decimal(f"{base_rate:.4f}"),
                        observed_value=Decimal(f"{curr_rate:.4f}"),
                        deviation_value=Decimal(f"{delta:.4f}"),
                        dimension="payment_method",
                        dimension_value=method,
                        severity=severity,
                        confidence=round(confidence, 4),
                        evidence={
                            "rule_id": self.rule_id,
                            "method": method,
                            "baseline_rate_pct": round(base_rate * 100, 2),
                            "current_rate_pct": round(curr_rate * 100, 2),
                            "drop_percentage_points": round(abs_drop * 100, 2),
                            "sample_size": curr_stat.get("total_count", 0),
                            "failed_transactions": curr_stat.get("failed_count", 0),
                        },
                    )
                )
        return signals


class FailureSpikeRule(DetectionRule):
    """Rule 2: Detects sudden spike in overall checkout failure rate."""

    def __init__(self, spike_threshold: float = 0.08) -> None:
        super().__init__(
            rule_id="RULE_002_FAILURE_SPIKE",
            name="Sudden Failure Spike",
            description="Detects anomalous surge in overall payment transaction failure rates.",
        )
        self.spike_threshold = spike_threshold

    def evaluate(self, current_data: dict[str, Any], baseline_data: dict[str, Any]) -> list[RiskSignalCreate]:
        curr_total = current_data.get("summary", {}).get("total_count", 0)
        if curr_total < 10:
            return []

        curr_fail_rate = 1.0 - current_data.get("summary", {}).get("success_rate", 1.0)
        base_fail_rate = 1.0 - baseline_data.get("summary", {}).get("success_rate", 0.95)

        fail_rate_increase = curr_fail_rate - base_fail_rate
        if fail_rate_increase >= self.spike_threshold:
            severity: RiskSeverity = "CRITICAL" if fail_rate_increase >= 0.18 else ("HIGH" if fail_rate_increase >= 0.10 else "MEDIUM")
            return [
                RiskSignalCreate(
                    signal_type="FAILURE_SPIKE",
                    metric_name="OVERALL_FAILURE_RATE",
                    baseline_value=Decimal(f"{base_fail_rate:.4f}"),
                    observed_value=Decimal(f"{curr_fail_rate:.4f}"),
                    deviation_value=Decimal(f"{fail_rate_increase:.4f}"),
                    dimension="overall",
                    dimension_value="all_methods",
                    severity=severity,
                    confidence=0.92,
                    evidence={
                        "rule_id": self.rule_id,
                        "baseline_failure_pct": round(base_fail_rate * 100, 2),
                        "current_failure_pct": round(curr_fail_rate * 100, 2),
                        "spike_percentage_points": round(fail_rate_increase * 100, 2),
                        "total_evaluated_transactions": curr_total,
                    },
                )
            ]
        return []


class VelocityAnomalyRule(DetectionRule):
    """Rule 3: Detects transaction velocity anomaly (high frequency failure bursts)."""

    def __init__(self, failure_velocity_threshold: int = 40) -> None:
        super().__init__(
            rule_id="RULE_003_VELOCITY_ANOMALY",
            name="Failure Velocity Anomaly",
            description="Flags anomalous velocity in failure occurrences within the evaluated time window.",
        )
        self.threshold = failure_velocity_threshold

    def evaluate(self, current_data: dict[str, Any], baseline_data: dict[str, Any]) -> list[RiskSignalCreate]:
        curr_failed = current_data.get("summary", {}).get("failed_count", 0)
        if curr_failed >= self.threshold:
            severity: RiskSeverity = "HIGH" if curr_failed >= 100 else "MEDIUM"
            return [
                RiskSignalCreate(
                    signal_type="VELOCITY_ANOMALY",
                    metric_name="FAILURE_VELOCITY",
                    baseline_value=Decimal("10.0000"),
                    observed_value=Decimal(f"{curr_failed:.4f}"),
                    deviation_value=Decimal(f"{curr_failed - 10:.4f}"),
                    dimension="time_window",
                    dimension_value="current_evaluation_window",
                    severity=severity,
                    confidence=0.88,
                    evidence={
                        "rule_id": self.rule_id,
                        "failed_count": curr_failed,
                        "threshold": self.threshold,
                        "window_minutes": current_data.get("window_minutes", 120),
                    },
                )
            ]
        return []


class RevenueAtRiskRule(DetectionRule):
    """Rule 4: Detects financial revenue exposure crossing material risk thresholds."""

    def __init__(self, threshold_inr: Decimal = Decimal("50000.00")) -> None:
        super().__init__(
            rule_id="RULE_004_REVENUE_AT_RISK",
            name="Revenue At Risk Exposure",
            description="Identifies accumulated uncollected revenue resulting from failed transactions.",
        )
        self.threshold_inr = threshold_inr

    def evaluate(self, current_data: dict[str, Any], baseline_data: dict[str, Any]) -> list[RiskSignalCreate]:
        failed_amount = current_data.get("summary", {}).get("failed_amount", Decimal("0.00"))
        if failed_amount >= self.threshold_inr:
            severity: RiskSeverity = "CRITICAL" if failed_amount >= Decimal("500000.00") else ("HIGH" if failed_amount >= Decimal("100000.00") else "MEDIUM")
            return [
                RiskSignalCreate(
                    signal_type="REVENUE_AT_RISK",
                    metric_name="UNCOLLECTED_REVENUE_VOLUME",
                    baseline_value=Decimal("0.0000"),
                    observed_value=failed_amount,
                    deviation_value=failed_amount,
                    dimension="financial",
                    dimension_value="INR",
                    severity=severity,
                    confidence=0.95,
                    evidence={
                        "rule_id": self.rule_id,
                        "revenue_at_risk_inr": float(failed_amount),
                        "threshold_inr": float(self.threshold_inr),
                    },
                )
            ]
        return []


class ConcentrationAnomalyRule(DetectionRule):
    """Rule 5: Detects abnormal failure concentration in a specific bank or gateway."""

    def __init__(self, concentration_threshold: float = 0.40) -> None:
        super().__init__(
            rule_id="RULE_005_CONCENTRATION_ANOMALY",
            name="Bank/Gateway Concentration Anomaly",
            description="Identifies localized issuer or gateway outages where failures disproportionately concentrate in a single bank.",
        )
        self.threshold = concentration_threshold

    def evaluate(self, current_data: dict[str, Any], baseline_data: dict[str, Any]) -> list[RiskSignalCreate]:
        signals: list[RiskSignalCreate] = []
        total_failed = current_data.get("summary", {}).get("failed_count", 0)
        if total_failed < 15:
            return []

        banks = current_data.get("banks", {})
        for bank_name, stat in banks.items():
            bank_failed = stat.get("failed_count", 0)
            share_of_failures = bank_failed / total_failed if total_failed > 0 else 0.0

            if share_of_failures >= self.threshold and bank_failed >= 10:
                severity: RiskSeverity = "HIGH" if share_of_failures >= 0.60 else "MEDIUM"
                signals.append(
                    RiskSignalCreate(
                        signal_type="CONCENTRATION_ANOMALY",
                        metric_name=f"{bank_name}_FAILURE_CONCENTRATION",
                        baseline_value=Decimal("0.2000"),
                        observed_value=Decimal(f"{share_of_failures:.4f}"),
                        deviation_value=Decimal(f"{share_of_failures - 0.20:.4f}"),
                        dimension="bank",
                        dimension_value=bank_name,
                        severity=severity,
                        confidence=0.94,
                        evidence={
                            "rule_id": self.rule_id,
                            "bank": bank_name,
                            "bank_failed_count": bank_failed,
                            "total_window_failures": total_failed,
                            "failure_share_pct": round(share_of_failures * 100, 2),
                        },
                    )
                )
        return signals


class ErrorCodeSpikeRule(DetectionRule):
    """Rule 6: Detects sudden spike in specific gateway or issuer error codes (e.g. GATEWAY_TIMEOUT)."""

    def __init__(self, error_share_threshold: float = 0.30) -> None:
        super().__init__(
            rule_id="RULE_006_ERROR_CODE_SPIKE",
            name="Error Code Surge",
            description="Flags anomalous frequency of specific technical error codes indicating upstream infrastructure problems.",
        )
        self.threshold = error_share_threshold

    def evaluate(self, current_data: dict[str, Any], baseline_data: dict[str, Any]) -> list[RiskSignalCreate]:
        signals: list[RiskSignalCreate] = []
        total_failed = current_data.get("summary", {}).get("failed_count", 0)
        if total_failed < 10:
            return []

        errors = current_data.get("errors", {})
        for error_code, count in errors.items():
            error_share = count / total_failed if total_failed > 0 else 0.0
            if error_share >= self.threshold and count >= 8:
                severity: RiskSeverity = "HIGH" if error_code == "GATEWAY_TIMEOUT" else "MEDIUM"
                signals.append(
                    RiskSignalCreate(
                        signal_type="ERROR_CODE_SPIKE",
                        metric_name=f"{error_code}_FREQUENCY",
                        baseline_value=Decimal("0.0500"),
                        observed_value=Decimal(f"{error_share:.4f}"),
                        deviation_value=Decimal(f"{error_share - 0.05:.4f}"),
                        dimension="error_code",
                        dimension_value=error_code,
                        severity=severity,
                        confidence=0.91,
                        evidence={
                            "rule_id": self.rule_id,
                            "error_code": error_code,
                            "error_count": count,
                            "total_failures": total_failed,
                            "error_share_pct": round(error_share * 100, 2),
                        },
                    )
                )
        return signals
