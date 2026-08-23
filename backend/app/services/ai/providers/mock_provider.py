"""Deterministic Mock AI Provider for offline development, tests, and demo environments."""

import time
from typing import Any
from app.services.ai.providers.base import AIProvider, AIProviderResult


class MockProvider(AIProvider):
    """Deterministic, evidence-grounded provider that formulates natural language answers from context."""

    def __init__(self, model: str = "recover-ai-deterministic-v1", timeout_seconds: float = 5.0):
        super().__init__(model=model, timeout_seconds=timeout_seconds)

    @property
    def provider_name(self) -> str:
        return "mock"

    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        context: dict[str, Any],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> AIProviderResult:
        """Formulate a grounded response based on context telemetry and prompt intent."""
        t0 = time.perf_counter()
        q = user_prompt.lower()

        # Extract verified facts from context
        case_info = context.get("case", {})
        metrics = context.get("metrics", {})
        root_cause = context.get("root_cause", {})
        impact = context.get("impact", {})
        evidence_list = context.get("evidence", [])
        recommendation = context.get("recommendation", {})

        total_tx = metrics.get("total_transactions", 1251)
        sr = metrics.get("overall_success_rate", 81.85)
        upi_sr = metrics.get("upi_success_rate", 72.09)
        hdfc_sr = metrics.get("hdfc_upi_success_rate", 64.77)
        primary_bank = metrics.get("primary_affected_bank", "HDFC")
        primary_method = metrics.get("primary_affected_payment_method", "UPI")
        dominant_err = metrics.get("dominant_error_code", "GATEWAY_TIMEOUT")
        dominant_err_cnt = metrics.get("dominant_error_count", 74)
        rev_at_risk = impact.get("revenue_at_risk_inr", "1,219,544.00")
        rec_rev = impact.get("recoverable_revenue_inr", "304,886.00")
        confidence = root_cause.get("confidence", 0.83)
        conf_pct = int(confidence * 100) if confidence <= 1.0 else int(confidence)
        primary_cause = root_cause.get("primary_cause", "Upstream HDFC UPI gateway timeout & latency degradation")

        # Intent handling
        if "did we recover" in q or ("how much" in q and "recovered" in q) or ("what" in q and "recovered" in q):
            text = (
                f"No recovery has been executed yet without explicit merchant authorization. "
                f"RecoverAI has recorded ₹1,28,400.00 in previously recovered revenue (54.8% recovery rate), "
                f"and currently estimates INR {rec_rev} as recoverable across {recommendation.get('eligible_transactions', 438)} eligible timeout-failed transactions in Batch RB-024."
            )
        elif "icici" in q:
            text = (
                f"Current verified telemetry does not indicate ICICI as the primary root cause. "
                f"While ICICI experienced isolated decline events, its success rate remained stable at 85.03%, "
                f"compared to {primary_bank}'s severe drop to {hdfc_sr:.2f}% with {dominant_err_cnt} timeouts."
            )
        elif "what should we do" in q or "recommend" in q or "next step" in q or "action" in q:
            text = (
                f"Based on current operational telemetry, your highest priority is Risk Case {case_info.get('case_reference', 'RC-001')} ({primary_method} Degradation).\n\n"
                f"• Active Investigation: Investigation {case_info.get('investigation_id', 'INV-00000000')} confirms {primary_cause} with {conf_pct}% confidence.\n"
                f"• Recommended Action: Review and authorize Recovery Batch RB-024.\n"
                f"• Target Scope: {recommendation.get('eligible_transactions', 438)} eligible timeout-failed transactions.\n"
                f"• Impact & Safeguards: Estimated recovery of INR {rec_rev} with an automatic 30.0% failure circuit breaker.\n"
                f"• Requirement: Action is proposal-only and REQUIRES merchant authorization before execution."
            )
        elif "why did upi" in q or "upi fail" in q or "why upi" in q:
            text = (
                f"UPI conversion dropped to {upi_sr:.2f}% (compared to a ~94.2% normal baseline, a -12.11 pp decline).\n\n"
                f"• Primary Vector: {primary_bank} UPI recorded a {hdfc_sr:.2f}% success rate with {dominant_err_cnt} '{dominant_err}' failures.\n"
                f"• Inferred Cause: {primary_cause} (Investigation Confidence: {conf_pct}%).\n"
                f"• Rail Stability: Card (95.44%) and NetBanking (94.51%) rails remain stable within SLA bounds."
            )
        elif "hdfc" in q or "affected bank" in q or ("why is" in q and "bank" in q):
            text = (
                f"{primary_bank} Bank is identified as the primary affected banking switch.\n\n"
                f"• Telemetry: Across {primary_bank} UPI traffic ({metrics.get('hdfc_upi_total', 298)} transactions), success rate dropped to {hdfc_sr:.2f}% with {metrics.get('hdfc_upi_failures', 105)} failures.\n"
                f"• Error Signature: '{dominant_err}' accounts for {dominant_err_cnt} failed attempts during upstream handle resolution.\n"
                f"• Peer Comparison: ICICI (85.03%), Axis (86.26%), and SBI (82.68%) maintained significantly higher conversion."
            )
        elif "how much revenue" in q or "revenue at risk" in q or "at risk" in q or "recoverable revenue" in q:
            text = (
                f"The financial exposure calculated for active incident {case_info.get('case_reference', 'RC-001')} is:\n\n"
                f"• Revenue at Risk: INR {rev_at_risk} (₹8.40L exposed in active case RC-001)\n"
                f"• Estimated Recoverable Revenue: INR {rec_rev}\n"
                f"• Target Scope: {recommendation.get('eligible_transactions', 438)} eligible timeout-failed transactions.\n"
                f"• Safety Policy: Single-retry limit with an automatic 30.0% failure circuit breaker."
            )
        elif "success rate" in q or "payment success" in q:
            text = (
                f"Overall payment success rate is currently {sr:.2f}%, down {metrics.get('success_rate_delta', -12.35):.2f} percentage points from the 94.20% baseline across {total_tx} transactions.\n\n"
                f"• Card Rail: 95.44% (Healthy)\n"
                f"• Net Banking Rail: 94.51% (Healthy)\n"
                f"• UPI Rail: {upi_sr:.2f}% (Degraded — Primary Incident Vector)"
            )
        elif "active risk cases" in q or "risk cases" in q or "how many risk cases" in q or "open risk cases" in q:
            text = (
                f"There is currently 1 active high-priority open risk case needing operational action: "
                f"**{case_info.get('case_reference', 'RC-001')}: {primary_method} Degradation** (₹8.40L exposed).\n\n"
                f"• Total Tracked Cases: 7 cases across historical reporting windows.\n"
                f"• Highest Priority: {case_info.get('case_reference', 'RC-001')} targeting {primary_bank} {primary_method} timeout failures."
            )
        elif "root cause" in q or "why is this happening" in q or "what caused" in q:
            text = (
                f"The primary root cause identified for investigation {case_info.get('investigation_id', 'INV-00000000')} is:\n\n"
                f"• Inferred Cause: {primary_cause} (Investigation Confidence: {conf_pct}%).\n"
                f"• Dominant Error: '{dominant_err}' ({dominant_err_cnt} occurrences on {primary_bank} {primary_method}).\n"
                f"• Hops Affected: Upstream bank handler resolution timeouts between 12:15 and 12:55 IST."
            )
        elif "failed transactions" in q or "how many transactions failed" in q or "failed tx" in q:
            text = (
                f"Out of {total_tx} total ingested transactions in the current incident window:\n\n"
                f"• Failed Transactions: 227 total failures (18.15% overall failure rate).\n"
                f"• Primary Concentration: 105 failures on {primary_bank} {primary_method} (74 attributed to '{dominant_err}').\n"
                f"• Recovery Eligibility: {recommendation.get('eligible_transactions', 438)} failed transactions across the incident window are verified eligible for retry."
            )
        elif "worst" in q or "performing worst" in q or "worst payment method" in q:
            text = (
                f"**{primary_method}** is currently the worst-performing payment method at a {upi_sr:.2f}% success rate "
                f"(compared to Card at 95.44% and Net Banking at 94.51%).\n\n"
                f"• Dominant Sub-Vector: {primary_bank} {primary_method} plunged to a {hdfc_sr:.2f}% success rate due to {dominant_err_cnt} '{dominant_err}' errors."
            )
        elif "error" in q and ("most" in q or "dominant" in q or "caused" in q or "failures" in q):
            text = (
                f"The dominant technical failure identified in this incident is '{dominant_err}'.\n\n"
                f"• Failure Concentration: '{dominant_err}' accounts for {dominant_err_cnt} failure events specifically on {primary_bank} {primary_method}.\n"
                f"• Impact: Upstream network hops timed out before receiving issuer authorization confirmation."
            )
        elif "summary" in q or "executive" in q or "brief" in q:
            text = (
                f"Executive Briefing for Incident {case_info.get('case_reference', 'RC-001')}:\n\n"
                f"• Incident: {primary_method} payment degradation primarily localized to {primary_bank} Bank switch.\n"
                f"• Overall Health: Success rate at {sr:.2f}% across {total_tx} transactions (UPI at {upi_sr:.2f}%).\n"
                f"• Root Cause: {primary_cause} ({conf_pct}% confidence).\n"
                f"• Business Impact: INR {rev_at_risk} at risk (INR {rec_rev} recoverable).\n"
                f"• Proposed Action: Bounded payment retry requiring operational approval."
            )
        else:
            text = (
                f"Investigation {case_info.get('investigation_id', 'INV-00000000')} diagnostic overview:\n\n"
                f"• Telemetry: {total_tx} total transactions ingested, overall conversion {sr:.2f}% (UPI: {upi_sr:.2f}%).\n"
                f"• Primary Vector: {primary_bank} {primary_method} ({hdfc_sr:.2f}% conversion, {dominant_err_cnt} '{dominant_err}' errors).\n"
                f"• Root Cause: {primary_cause} ({conf_pct}% confidence).\n"
                f"• Financial Impact: INR {rev_at_risk} at risk, INR {rec_rev} recoverable."
            )


        latency_ms = int((time.perf_counter() - t0) * 1000)
        return AIProviderResult(
            text=text,
            provider=self.provider_name,
            model=self.model,
            latency_ms=latency_ms,
            token_usage={"prompt_tokens": 180, "completion_tokens": 95, "total_tokens": 275},
            raw_payload={"mock": True},
        )
