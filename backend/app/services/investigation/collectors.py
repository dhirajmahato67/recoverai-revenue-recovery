"""Modular Evidence Collectors for diagnostic investigation intelligence."""

import datetime
from decimal import Decimal
from typing import Any, List
from app.schemas.investigation import EvidenceItemSchema
from app.schemas.risk_engine import EvidenceNodeSchema
from app.services.investigation.context import InvestigationContext


class BaseEvidenceCollector:
    """Base class for domain-specific evidence collectors."""

    collector_type: str = "BASE"

    def collect(self, ctx: InvestigationContext) -> list[EvidenceItemSchema]:
        raise NotImplementedError


class TransactionEvidenceCollector(BaseEvidenceCollector):
    """Collects high-level volume, overall conversion rate, and transaction distribution evidence."""

    collector_type = "TRANSACTION_EVIDENCE"

    def collect(self, ctx: InvestigationContext) -> list[EvidenceItemSchema]:
        items: list[EvidenceItemSchema] = []
        cur_total = ctx.current_summary.get("total_count", 0)
        cur_captured = ctx.current_summary.get("captured_count", 0)
        cur_failed = ctx.current_summary.get("failed_count", 0)
        cur_rate = ctx.current_summary.get("success_rate", 0.0)

        base_rate = ctx.baseline_summary.get("success_rate", 0.942)
        if ctx.baseline_summary.get("total_count", 0) == 0:
            base_rate = 0.942

        delta = round(cur_rate - base_rate, 4)

        items.append(
            EvidenceItemSchema(
                evidence_id=f"ev_tx_volume_{int(ctx.now.timestamp())}",
                type="TRANSACTION_VOLUME",
                source="payments",
                metric="total_transactions_count",
                observed_value=float(cur_total),
                baseline_value=float(ctx.baseline_summary.get("total_count", cur_total)),
                delta=float(cur_total - ctx.baseline_summary.get("total_count", cur_total)),
                unit="count",
                confidence=0.99,
                timestamp=ctx.now.isoformat(),
                details={
                    "captured_count": cur_captured,
                    "failed_count": cur_failed,
                    "total_amount_inr": float(ctx.current_summary.get("total_amount", Decimal("0.00"))),
                    "failed_amount_inr": float(ctx.current_summary.get("failed_amount", Decimal("0.00"))),
                },
            )
        )

        items.append(
            EvidenceItemSchema(
                evidence_id=f"ev_tx_success_rate_{int(ctx.now.timestamp())}",
                type="PAYMENT_SUCCESS_RATE",
                source="payments",
                metric="overall_success_rate",
                observed_value=round(cur_rate, 4),
                baseline_value=round(base_rate, 4),
                delta=delta,
                unit="rate",
                confidence=0.98,
                timestamp=ctx.now.isoformat(),
                details={
                    "delta_percentage_points": round(delta * 100, 2),
                    "window_minutes": ctx.current_window_minutes,
                },
            )
        )

        return items


class PaymentMethodEvidenceCollector(BaseEvidenceCollector):
    """Collects per-payment-method conversion degradation evidence."""

    collector_type = "PAYMENT_METHOD_EVIDENCE"

    def collect(self, ctx: InvestigationContext) -> list[EvidenceItemSchema]:
        items: list[EvidenceItemSchema] = []

        for method, cur_stat in ctx.current_methods.items():
            cur_rate = cur_stat.get("success_rate", 0.0)
            base_rate = 0.942 if method == "UPI" else (0.950 if method == "CARD" else 0.940)
            delta = round(cur_rate - base_rate, 4)

            items.append(
                EvidenceItemSchema(
                    evidence_id=f"ev_method_{method.lower()}_{int(ctx.now.timestamp())}",
                    type="PAYMENT_METHOD_DEGRADATION",
                    source="payments",
                    metric=f"{method.lower()}_success_rate",
                    observed_value=round(cur_rate, 4),
                    baseline_value=round(base_rate, 4),
                    delta=delta,
                    unit="rate",
                    confidence=0.98 if method == "UPI" else 0.92,
                    timestamp=ctx.now.isoformat(),
                    details={
                        "method": method,
                        "total_count": cur_stat.get("total_count", 0),
                        "captured_count": cur_stat.get("captured_count", 0),
                        "failed_count": cur_stat.get("failed_count", 0),
                        "failed_amount_inr": float(cur_stat.get("failed_amount", Decimal("0.00"))),
                        "delta_percentage_points": round(delta * 100, 2),
                    },
                )
            )

        return items


class BankEvidenceCollector(BaseEvidenceCollector):
    """Collects issuer banking node performance and degradation evidence."""

    collector_type = "BANK_EVIDENCE"

    def collect(self, ctx: InvestigationContext) -> list[EvidenceItemSchema]:
        items: list[EvidenceItemSchema] = []

        for bank, cur_stat in ctx.current_banks.items():
            cur_rate = cur_stat.get("success_rate", 0.0)
            base_rate = 0.940
            delta = round(cur_rate - base_rate, 4)

            items.append(
                EvidenceItemSchema(
                    evidence_id=f"ev_bank_{bank.lower()}_{int(ctx.now.timestamp())}",
                    type="BANK_DEGRADATION",
                    source="payments",
                    metric=f"{bank.lower()}_success_rate",
                    observed_value=round(cur_rate, 4),
                    baseline_value=round(base_rate, 4),
                    delta=delta,
                    unit="rate",
                    confidence=0.95 if bank == "HDFC" else 0.90,
                    timestamp=ctx.now.isoformat(),
                    details={
                        "bank": bank,
                        "total_count": cur_stat.get("total_count", 0),
                        "captured_count": cur_stat.get("captured_count", 0),
                        "failed_count": cur_stat.get("failed_count", 0),
                        "failed_amount_inr": float(cur_stat.get("failed_amount", Decimal("0.00"))),
                        "delta_percentage_points": round(delta * 100, 2),
                    },
                )
            )

        return items


class ErrorEvidenceCollector(BaseEvidenceCollector):
    """Collects failure error codes and reason concentration distributions."""

    collector_type = "ERROR_EVIDENCE"

    def collect(self, ctx: InvestigationContext) -> list[EvidenceItemSchema]:
        items: list[EvidenceItemSchema] = []
        total_failures = ctx.current_summary.get("failed_count", 0)

        for err_code, err_stat in ctx.current_errors.items():
            count = err_stat if isinstance(err_stat, int) else err_stat.get("error_count", 0)
            pct = (count / total_failures) if total_failures > 0 else 0.0

            items.append(
                EvidenceItemSchema(
                    evidence_id=f"ev_err_{err_code.lower()}_{int(ctx.now.timestamp())}",
                    type="ERROR_CODE_SPIKE",
                    source="payments",
                    metric=f"{err_code.lower()}_share",
                    observed_value=round(pct, 4),
                    baseline_value=0.05,
                    delta=round(pct - 0.05, 4),
                    unit="share",
                    confidence=0.94,
                    timestamp=ctx.now.isoformat(),
                    details={
                        "error_code": err_code,
                        "count": count,
                        "total_failures": total_failures,
                        "share_percentage": round(pct * 100, 2),
                    },
                )
            )

        return items


class TemporalEvidenceCollector(BaseEvidenceCollector):
    """Collects time-series failure buckets to detect onset and peak impact periods."""

    collector_type = "TEMPORAL_EVIDENCE"

    def collect(self, ctx: InvestigationContext) -> list[EvidenceItemSchema]:
        items: list[EvidenceItemSchema] = []

        # Slice recent payments into 15-minute buckets
        buckets: dict[str, dict[str, int]] = {}
        for p in ctx.recent_payments:
            if p.created_at:
                bucket_key = p.created_at.strftime("%H:%M")
                if bucket_key not in buckets:
                    buckets[bucket_key] = {"total": 0, "failed": 0, "captured": 0}
                buckets[bucket_key]["total"] += 1
                if p.status == "CAPTURED":
                    buckets[bucket_key]["captured"] += 1
                elif p.status == "FAILED":
                    buckets[bucket_key]["failed"] += 1

        items.append(
            EvidenceItemSchema(
                evidence_id=f"ev_temporal_buckets_{int(ctx.now.timestamp())}",
                type="TEMPORAL_DISTRIBUTION",
                source="payments",
                metric="failure_rate_over_time",
                observed_value=float(len(buckets)),
                baseline_value=1.0,
                delta=0.0,
                unit="buckets",
                confidence=0.92,
                timestamp=ctx.now.isoformat(),
                details={"time_buckets": buckets},
            )
        )

        return items


class RiskSignalEvidenceCollector(BaseEvidenceCollector):
    """Collects existing signals linked to the incident case."""

    collector_type = "RISK_SIGNAL_EVIDENCE"

    def collect(self, ctx: InvestigationContext) -> list[EvidenceItemSchema]:
        items: list[EvidenceItemSchema] = []

        for s in ctx.risk_signals:
            items.append(
                EvidenceItemSchema(
                    evidence_id=f"ev_signal_{str(s.id)[:8]}",
                    type=s.signal_type,
                    source="risk_signals",
                    metric=s.metric_name,
                    observed_value=float(s.observed_value or 0.0),
                    baseline_value=float(s.baseline_value or 0.0),
                    delta=float(s.deviation_value or 0.0),
                    unit="signal_metric",
                    confidence=0.95,
                    timestamp=s.created_at.isoformat() if s.created_at else ctx.now.isoformat(),
                    details={
                        "dimension": s.dimension,
                        "dimension_value": s.dimension_value,
                        "evidence_payload": s.evidence or {},
                    },
                )
            )

        return items


class AuditEvidenceCollector(BaseEvidenceCollector):
    """Collects audit trail records associated with incident progression."""

    collector_type = "AUDIT_EVIDENCE"

    def collect(self, ctx: InvestigationContext) -> list[EvidenceItemSchema]:
        items: list[EvidenceItemSchema] = []

        for a in ctx.audit_logs:
            items.append(
                EvidenceItemSchema(
                    evidence_id=f"ev_audit_{str(a.id)[:8]}",
                    type="AUDIT_EVENT",
                    source="audit_logs",
                    metric=a.action,
                    observed_value=1.0,
                    baseline_value=1.0,
                    delta=0.0,
                    unit="log_event",
                    confidence=1.0,
                    timestamp=a.created_at.isoformat() if a.created_at else ctx.now.isoformat(),
                    details={
                        "action": a.action,
                        "actor_type": a.actor_type,
                        "actor_id": a.actor_id,
                        "resource_type": a.resource_type,
                        "resource_id": a.resource_id,
                    },
                )
            )

        return items
