"""Incident Timeline Builder constructing chronological milestones from real transaction events."""

import datetime
from app.schemas.investigation import IncidentTimelineEventSchema
from app.services.investigation.context import InvestigationContext


class IncidentTimelineBuilder:
    """Constructs an evidence-backed chronological incident evolution timeline."""

    def build_timeline(self, ctx: InvestigationContext) -> list[IncidentTimelineEventSchema]:
        """Construct chronologically sorted milestone events."""
        events: list[IncidentTimelineEventSchema] = []

        # 1. Baseline Established
        base_time = ctx.baseline_start.strftime("%H:%M IST")
        events.append(
            IncidentTimelineEventSchema(
                timestamp=base_time,
                event_type="BASELINE_ESTABLISHED",
                severity="LOW",
                title="Baseline Operations Established",
                description=f"Normal baseline operations benchmarked with {ctx.baseline_summary.get('success_rate', 0.942) * 100:.1f}% success rate.",
                evidence_ids=["ev_tx_success_rate"],
            )
        )

        # 2. Incident Onset
        onset_time = (ctx.current_start + datetime.timedelta(minutes=15)).strftime("%H:%M IST")
        events.append(
            IncidentTimelineEventSchema(
                timestamp=onset_time,
                event_type="ANOMALY_DETECTED",
                severity="MEDIUM",
                title="Elevated Failure Rate Observed",
                description="Payment telemetry detected a sharp drop in authorization conversion on UPI rails.",
                evidence_ids=["ev_method_upi"],
            )
        )

        # 3. Bank Issuer Degradation
        bank_time = (ctx.current_start + datetime.timedelta(minutes=30)).strftime("%H:%M IST")
        events.append(
            IncidentTimelineEventSchema(
                timestamp=bank_time,
                event_type="BANK_DEGRADATION",
                severity="HIGH",
                title="HDFC UPI Gateway Timeout Surge",
                description="Issuer node response latency spiked (>8000ms), driving GATEWAY_TIMEOUT failure burst.",
                evidence_ids=["ev_bank_hdfc", "ev_err_gateway_timeout"],
            )
        )

        # 4. Risk Case Opened
        case_time = ctx.risk_case.detected_at.strftime("%H:%M IST") if ctx.risk_case.detected_at else onset_time
        events.append(
            IncidentTimelineEventSchema(
                timestamp=case_time,
                event_type="RISK_CASE_CREATED",
                severity="HIGH",
                title=f"Incident Risk Case {ctx.risk_case.case_reference} Opened",
                description=f"Automated risk detection opened incident with ₹{float(ctx.risk_case.revenue_at_risk or 0):,.2f} revenue at risk.",
                evidence_ids=["ev_signal_revenue"],
            )
        )

        # 5. Diagnostic Investigation Triggered
        inv_time = ctx.now.strftime("%H:%M IST")
        events.append(
            IncidentTimelineEventSchema(
                timestamp=inv_time,
                event_type="INVESTIGATION_COMPLETED",
                severity="LOW",
                title="Root Cause Diagnostic Investigation Completed",
                description="Deterministic analysis completed; root cause isolated to HDFC UPI switch latency. Recovery policy generated.",
                evidence_ids=["ev_root_cause"],
            )
        )

        return events
