"""Deterministic Risk Scoring Engine for RecoverAI."""

from decimal import Decimal
from typing import Any
from app.schemas.risk_engine import RiskSeverity, RiskSignalCreate


class RiskScoringEngine:
    """Calculates deterministic composite incident risk scores (0-100) and classifications."""

    @classmethod
    def calculate_score(
        cls,
        signals: list[RiskSignalCreate],
        current_data: dict[str, Any],
        baseline_data: dict[str, Any],
    ) -> tuple[float, RiskSeverity]:
        """Compute deterministic composite score across degradation, velocity, concentration, and revenue."""
        if not signals:
            return 0.0, "LOW"

        # 1. Degradation component (0 - 30 pts)
        degradation_score = 0.0
        for s in signals:
            if s.signal_type == "PAYMENT_METHOD_DEGRADATION" and s.deviation_value:
                drop_frac = abs(float(s.deviation_value))
                # 20% drop yields full 30 pts
                degradation_score = max(degradation_score, min(30.0, (drop_frac / 0.20) * 30.0))

        # 2. Failure spike component (0 - 25 pts)
        failure_spike_score = 0.0
        for s in signals:
            if s.signal_type == "FAILURE_SPIKE" and s.deviation_value:
                spike_frac = float(s.deviation_value)
                failure_spike_score = min(25.0, (spike_frac / 0.15) * 25.0)

        # 3. Velocity component (0 - 15 pts)
        velocity_score = 0.0
        for s in signals:
            if s.signal_type == "VELOCITY_ANOMALY":
                failed_count = s.evidence.get("failed_count", 0)
                velocity_score = min(15.0, (failed_count / 100.0) * 15.0)

        # 4. Concentration component (0 - 15 pts)
        concentration_score = 0.0
        for s in signals:
            if s.signal_type in ["CONCENTRATION_ANOMALY", "ERROR_CODE_SPIKE"]:
                concentration_score = max(concentration_score, 12.0 if s.severity == "HIGH" else 8.0)

        # 5. Revenue impact component (0 - 15 pts)
        revenue_score = 0.0
        failed_amt = current_data.get("summary", {}).get("failed_amount", Decimal("0.00"))
        if failed_amt > Decimal("0.00"):
            # ₹5,00,000 uncollected yields full 15 pts
            revenue_score = min(15.0, (float(failed_amt) / 500000.0) * 15.0)

        total_score = min(100.0, degradation_score + failure_spike_score + velocity_score + concentration_score + revenue_score)
        total_score = round(total_score, 1)

        # Classify severity band
        if total_score >= 80.0:
            severity: RiskSeverity = "CRITICAL"
        elif total_score >= 60.0:
            severity = "HIGH"
        elif total_score >= 30.0:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        return total_score, severity
