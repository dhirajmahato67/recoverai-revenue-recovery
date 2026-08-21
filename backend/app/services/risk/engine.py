"""Risk Detection Engine orchestrating rule evaluation, risk scoring, and case creation."""

import datetime
import time
import uuid
from decimal import Decimal
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.models import AuditLog, RiskCase, RiskSignal
from app.db.repositories.payment import PaymentRepository
from app.db.repositories.risk_case import RiskCaseRepository
from app.schemas.risk_engine import (
    RiskAnalysisRequest,
    RiskAnalysisResponse,
    RiskSeverity,
    RiskSignalCreate,
)
from app.services.risk.rules import (
    ConcentrationAnomalyRule,
    DetectionRule,
    ErrorCodeSpikeRule,
    FailureSpikeRule,
    PaymentMethodDegradationRule,
    RevenueAtRiskRule,
    VelocityAnomalyRule,
)
from app.services.risk.scoring import RiskScoringEngine

logger = get_logger("app.services.risk.engine")


class RiskDetectionEngine:
    """Production-grade telemetry risk detection engine analyzing live and historical transactions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.payment_repo = PaymentRepository(session)
        self.risk_case_repo = RiskCaseRepository(session)
        self.settings = get_settings()

        # Initialize modular detection rules
        self.rules: list[DetectionRule] = [
            PaymentMethodDegradationRule(drop_threshold=self.settings.RISK_DEGRADATION_THRESHOLD),
            FailureSpikeRule(spike_threshold=self.settings.RISK_FAILURE_SPIKE_THRESHOLD),
            VelocityAnomalyRule(failure_velocity_threshold=self.settings.RISK_VELOCITY_THRESHOLD),
            RevenueAtRiskRule(threshold_inr=Decimal("50000.00")),
            ConcentrationAnomalyRule(concentration_threshold=0.40),
            ErrorCodeSpikeRule(error_share_threshold=0.30),
        ]

    async def analyze(
        self,
        request: RiskAnalysisRequest,
        request_id: str | None = None,
    ) -> RiskAnalysisResponse:
        """Execute risk detection rules against historical and active transaction windows."""
        start_time = time.perf_counter()
        now = datetime.datetime.now(datetime.timezone.utc)

        current_window_start = now - datetime.timedelta(minutes=request.current_window_minutes)
        baseline_window_start = now - datetime.timedelta(minutes=request.baseline_window_minutes)

        # 1. Fetch live operational telemetry
        current_summary = await self.payment_repo.get_window_summary(
            request.merchant_id, current_window_start, now
        )
        baseline_summary = await self.payment_repo.get_window_summary(
            request.merchant_id, baseline_window_start, now
        )

        current_methods = await self.payment_repo.get_window_method_breakdown(
            request.merchant_id, current_window_start, now
        )
        baseline_methods = await self.payment_repo.get_window_method_breakdown(
            request.merchant_id, baseline_window_start, now
        )

        current_banks = await self.payment_repo.get_window_bank_breakdown(
            request.merchant_id, current_window_start, now
        )
        baseline_banks = await self.payment_repo.get_window_bank_breakdown(
            request.merchant_id, baseline_window_start, now
        )

        current_errors = await self.payment_repo.get_window_error_breakdown(
            request.merchant_id, current_window_start, now
        )

        current_data = {
            "window_minutes": request.current_window_minutes,
            "summary": current_summary,
            "methods": current_methods,
            "banks": current_banks,
            "errors": current_errors,
        }

        baseline_data = {
            "window_minutes": request.baseline_window_minutes,
            "summary": baseline_summary,
            "methods": baseline_methods,
            "banks": baseline_banks,
        }

        # 2. Evaluate all modular rules
        detected_signals: list[RiskSignalCreate] = []
        for rule in self.rules:
            rule_signals = rule.evaluate(current_data, baseline_data)
            detected_signals.extend(rule_signals)

        # 3. Calculate composite risk score & severity
        composite_score, severity = RiskScoringEngine.calculate_score(
            detected_signals, current_data, baseline_data
        )

        curr_success_rate = current_summary.get("success_rate", 1.0)
        base_success_rate = baseline_summary.get("success_rate", 1.0)
        success_rate_delta = curr_success_rate - base_success_rate

        revenue_at_risk = float(current_summary.get("failed_amount", Decimal("0.00")))
        # Recoverable revenue estimation: 25% of uncollected revenue
        recoverable_revenue = round(revenue_at_risk * 0.25, 2)

        risk_case_created = False
        persisted_case_id: uuid.UUID | None = None
        case_ref: str | None = None

        # 4. Group signals and create or update RiskCase if signals detected and not dry_run
        if detected_signals and not request.dry_run:
            persisted_case_id, case_ref, risk_case_created = await self._persist_risk_incident(
                merchant_id=request.merchant_id,
                signals=detected_signals,
                severity=severity,
                revenue_at_risk=Decimal(f"{revenue_at_risk:.2f}"),
                recoverable_revenue=Decimal(f"{recoverable_revenue:.2f}"),
                current_data=current_data,
                request_id=request_id,
            )

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Risk analysis evaluated for merchant {request.merchant_id}: "
            f"{len(detected_signals)} signals, score={composite_score}, severity={severity} in {duration_ms:.2f}ms"
        )

        return RiskAnalysisResponse(
            merchant_id=request.merchant_id,
            evaluated_at=now,
            current_window_transactions=current_summary.get("total_count", 0),
            baseline_window_transactions=baseline_summary.get("total_count", 0),
            current_success_rate=round(curr_success_rate, 4),
            baseline_success_rate=round(base_success_rate, 4),
            success_rate_delta=round(success_rate_delta, 4),
            signals_detected_count=len(detected_signals),
            signals=detected_signals,
            composite_risk_score=composite_score,
            severity=severity,
            risk_case_created=risk_case_created,
            risk_case_id=persisted_case_id,
            case_reference=case_ref,
            revenue_at_risk=revenue_at_risk,
            recoverable_revenue=recoverable_revenue,
            duration_ms=round(duration_ms, 2),
        )

    async def _persist_risk_incident(
        self,
        merchant_id: uuid.UUID,
        signals: list[RiskSignalCreate],
        severity: RiskSeverity,
        revenue_at_risk: Decimal,
        recoverable_revenue: Decimal,
        current_data: dict[str, Any],
        request_id: str | None = None,
    ) -> tuple[uuid.UUID, str, bool]:
        """Group signals and persist a single cohesive RiskCase and associated RiskSignals."""
        # Determine primary incident characteristics
        has_upi_drop = any(
            (s.dimension_value in ["UPI", "HDFC"] or "UPI" in s.metric_name or "HDFC" in s.metric_name)
            for s in signals
        )
        risk_type = "PAYMENT_DEGRADATION"
        title = "UPI payment degradation" if has_upi_drop else "Payment success rate degradation"
        summary = (
            f"Automated risk detection identified significant payment degradation. "
            f"{len(signals)} risk signals detected with estimated uncollected revenue exposure of INR {revenue_at_risk:,.2f}."
        )

        # Check for existing open case to prevent duplicate spam
        existing_cases_stmt = (
            select(RiskCase)
            .where(
                RiskCase.merchant_id == merchant_id,
                RiskCase.risk_type == risk_type,
                RiskCase.status.in_(["OPEN", "INVESTIGATING", "RECOMMENDED"]),
            )
            .order_by(RiskCase.detected_at.desc())
        )
        existing_case = (await self.session.execute(existing_cases_stmt)).scalars().first()

        avg_confidence = (
            sum(s.confidence for s in signals) / len(signals) if signals else 0.90
        )
        conf_decimal = Decimal(f"{avg_confidence:.4f}")

        is_new_case = False
        if existing_case:
            target_case = existing_case
            target_case.revenue_at_risk = max(target_case.revenue_at_risk, revenue_at_risk)
            target_case.estimated_recoverable_revenue = max(
                target_case.estimated_recoverable_revenue, recoverable_revenue
            )
            target_case.severity = severity
            target_case.summary = summary
            target_case.confidence_score = conf_decimal
            case_id = target_case.id
            case_ref = target_case.case_reference
        else:
            case_id = uuid.uuid4()
            # Count existing cases for friendly reference number
            count_stmt = select(RiskCase).where(RiskCase.merchant_id == merchant_id)
            total_cases = len((await self.session.execute(count_stmt)).scalars().all())
            case_ref = f"RC-{total_cases + 1:03d}"

            target_case = RiskCase(
                id=case_id,
                merchant_id=merchant_id,
                case_reference=case_ref,
                risk_type=risk_type,
                severity=severity,
                status="OPEN",
                title=title,
                summary=summary,
                revenue_at_risk=revenue_at_risk,
                estimated_recoverable_revenue=recoverable_revenue,
                confidence_score=conf_decimal,
                detected_at=datetime.datetime.now(datetime.timezone.utc),
            )
            self.session.add(target_case)
            is_new_case = True

        await self.session.flush()

        # Persist new telemetry signals associated with the case
        for s in signals:
            signal_entity = RiskSignal(
                risk_case_id=case_id,
                signal_type=s.signal_type,
                metric_name=s.metric_name,
                baseline_value=s.baseline_value,
                observed_value=s.observed_value,
                deviation_value=s.deviation_value,
                dimension=s.dimension,
                dimension_value=s.dimension_value,
                evidence=s.evidence,
            )
            self.session.add(signal_entity)

        # Audit Log
        audit_log = AuditLog(
            merchant_id=merchant_id,
            actor_type="AI_AGENT",
            actor_id="risk_detection_engine_v1",
            action="RISK_DETECTED",
            resource_type="RiskCase",
            resource_id=case_ref,
            request_id=request_id,
            metadata_={
                "risk_case_id": str(case_id),
                "case_reference": case_ref,
                "signals_count": len(signals),
                "severity": severity,
                "revenue_at_risk": float(revenue_at_risk),
            },
        )
        self.session.add(audit_log)
        await self.session.commit()

        return case_id, case_ref, is_new_case
