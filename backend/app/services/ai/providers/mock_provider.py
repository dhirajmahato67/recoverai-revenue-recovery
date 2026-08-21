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
        if ("already" in q and "recover" in q) or ("how much" in q and "recovered" in q) or ("did we recover" in q):
            text = (
                f"No recovery has been executed yet. In accordance with safety policies, direct recovery requires "
                f"explicit merchant financial authorization. The system currently estimates INR {rec_rev} as recoverable."
            )
        elif "error" in q and ("most" in q or "dominant" in q or "caused" in q or "failures" in q):
            text = (
                f"The dominant technical failure identified in this incident is '{dominant_err}'.\n\n"
                f"• Failure Concentration: '{dominant_err}' accounts for {dominant_err_cnt} failure events specifically on {primary_bank} {primary_method}.\n"
                f"• Impact: Upstream network hops timed out before receiving issuer authorization confirmation."
            )
        elif "why did upi" in q or "upi fail" in q or "what caused" in q or ("root cause" in q and "what is" in q):
            text = (
                f"Based on verified telemetry for investigation {case_info.get('investigation_id', 'INV-00000000')}, "
                f"UPI conversion dropped to {upi_sr:.2f}% (normal baseline: ~94%).\n\n"
                f"• Observed Fact: {primary_bank} UPI recorded {hdfc_sr:.2f}% success rate with {dominant_err_cnt} '{dominant_err}' failures.\n"
                f"• Inferred Cause: {primary_cause} (Investigation Confidence: {conf_pct}%).\n"
                f"• Rail Stability: Card (95.44%) and NetBanking (94.51%) rails remained stable within SLA bounds."
            )
        elif "hdfc" in q or "affected bank" in q or ("why is" in q and "bank" in q):
            text = (
                f"{primary_bank} Bank is identified as the primary affected banking switch. "
                f"Across {primary_bank} UPI traffic ({metrics.get('hdfc_upi_total', 298)} transactions), success rate dropped to {hdfc_sr:.2f}% with {metrics.get('hdfc_upi_failures', 105)} failures.\n\n"
                f"• Dominant Failure: '{dominant_err}' accounts for {dominant_err_cnt} failed attempts.\n"
                f"• Comparative Context: ICICI (85.03%), SBI (82.68%), and AXIS (86.26%) experienced significantly lower degradation."
            )
        elif "icici" in q:
            text = (
                f"Current verified telemetry does not indicate ICICI as the primary root cause. "
                f"While ICICI experienced isolated decline events, its success rate remained stable at 85.03%, compared to {primary_bank}'s severe drop to {hdfc_sr:.2f}% with {dominant_err_cnt} timeouts."
            )
        elif "recoverable" in q and ("revenue" in q or "what is" in q or "how much" in q):
            text = (
                f"The estimated recoverable revenue for incident {case_info.get('case_reference', 'RC-001')} is INR {rec_rev}.\n\n"
                f"• Target Scope: Eligible failed transactions exhibiting transient upstream timeouts.\n"
                f"• Safety Policy: Capped exposure of INR {rec_rev} with an automatic 30.0% failure circuit breaker."
            )
        elif "revenue" in q or "risk" in q or "money" in q or "financial" in q or "cost" in q:
            text = (
                f"The financial exposure calculated for this incident is:\n\n"
                f"• Revenue at Risk: INR {rev_at_risk}\n"
                f"• Estimated Recoverable Revenue: INR {rec_rev}\n"
                f"• Bounded Policy Limit: 1 retry attempt with an automatic 30.0% failure circuit breaker.\n\n"
                f"Note: All revenue figures are strictly calculated via database telemetry using Decimal precision."
            )
        elif "what should we do" in q or "recommend" in q or "next step" in q or "action" in q:
            text = (
                f"RecoverAI recommends formulating a bounded PAYMENT_RETRY recovery batch:\n\n"
                f"• Strategy: Target {recommendation.get('eligible_transactions', 438)} eligible timeout-failed transactions.\n"
                f"• Safeguards: Max exposure capped at INR {rec_rev}, stopping condition set to '{recommendation.get('stopping_condition', 'Failure rate exceeds 30%')}'.\n"
                f"• Authorization: Action is proposal-only (can_execute=false) and REQUIRES merchant authorization."
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
