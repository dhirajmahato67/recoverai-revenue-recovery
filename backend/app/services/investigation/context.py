"""Investigation Context providing optimized, single-pass telemetry data to all collectors."""

import datetime
import uuid
from decimal import Decimal
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditLog, Payment, PaymentEvent, RiskCase, RiskSignal
from app.db.repositories.payment import PaymentRepository


class InvestigationContext:
    """Context object bundling pre-queried telemetry for an investigation session."""

    def __init__(
        self,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        risk_case: RiskCase,
        current_window_minutes: int = 120,
        baseline_window_minutes: int = 1440,
    ) -> None:
        self.session = session
        self.merchant_id = merchant_id
        self.risk_case = risk_case
        self.current_window_minutes = current_window_minutes
        self.baseline_window_minutes = baseline_window_minutes

        # Calculated window timestamps
        self.now = datetime.datetime.now(datetime.timezone.utc)
        self.current_start = self.now - datetime.timedelta(minutes=current_window_minutes)
        self.baseline_start = self.now - datetime.timedelta(minutes=baseline_window_minutes)

        # Cached telemetry data
        self.current_summary: dict[str, Any] = {}
        self.baseline_summary: dict[str, Any] = {}
        self.current_methods: dict[str, dict[str, Any]] = {}
        self.baseline_methods: dict[str, dict[str, Any]] = {}
        self.current_banks: dict[str, dict[str, Any]] = {}
        self.baseline_banks: dict[str, dict[str, Any]] = {}
        self.current_errors: dict[str, dict[str, Any]] = {}
        self.method_bank_breakdown: list[dict[str, Any]] = []
        self.recent_payments: list[Payment] = []
        self.risk_signals: list[RiskSignal] = []
        self.audit_logs: list[AuditLog] = []

    async def initialize(self) -> "InvestigationContext":
        """Pre-fetch all necessary data in optimized SQL queries scoped deterministically to transaction bounds."""
        payment_repo = PaymentRepository(self.session)

        # Authoritative transaction dataset bounds
        min_tx, max_tx = await payment_repo.get_merchant_transaction_bounds(self.merchant_id)

        if min_tx is not None and max_tx is not None:
            self.now = max_tx
            self.current_start = min_tx
            self.baseline_start = min_tx
        else:
            # Fallback if no transactions exist in the tenant yet
            anchor = self.risk_case.detected_at or datetime.datetime.now(datetime.timezone.utc)
            self.now = anchor
            self.current_start = self.now - datetime.timedelta(minutes=self.current_window_minutes)
            self.baseline_start = self.now - datetime.timedelta(minutes=self.baseline_window_minutes)

        # 1. Summaries
        self.current_summary = await payment_repo.get_window_summary(
            self.merchant_id, self.current_start, self.now
        )
        self.baseline_summary = await payment_repo.get_window_summary(
            self.merchant_id, self.baseline_start, self.now
        )

        # 2. Method breakdowns
        self.current_methods = await payment_repo.get_window_method_breakdown(
            self.merchant_id, self.current_start, self.now
        )
        self.baseline_methods = await payment_repo.get_window_method_breakdown(
            self.merchant_id, self.baseline_start, self.now
        )

        # 3. Bank breakdowns
        self.current_banks = await payment_repo.get_window_bank_breakdown(
            self.merchant_id, self.current_start, self.now
        )
        self.baseline_banks = await payment_repo.get_window_bank_breakdown(
            self.merchant_id, self.baseline_start, self.now
        )

        # 4. Error breakdowns
        self.current_errors = await payment_repo.get_window_error_breakdown(
            self.merchant_id, self.current_start, self.now
        )

        # 5. Method + Bank granular breakdowns
        self.method_bank_breakdown = await payment_repo.get_window_method_bank_breakdown(
            self.merchant_id, self.current_start, self.now
        )

        # 6. Raw recent failed and captured payments for timeline & impact slicing (limit 500)
        stmt_payments = (
            select(Payment)
            .where(
                Payment.merchant_id == self.merchant_id,
                Payment.created_at >= self.current_start,
                Payment.created_at <= self.now,
            )
            .order_by(Payment.created_at.desc())
            .limit(500)
        )
        self.recent_payments = list((await self.session.execute(stmt_payments)).scalars().all())

        # 6. Risk signals for this case
        stmt_signals = (
            select(RiskSignal)
            .where(RiskSignal.risk_case_id == self.risk_case.id)
            .order_by(RiskSignal.created_at.desc())
        )
        self.risk_signals = list((await self.session.execute(stmt_signals)).scalars().all())

        # 7. Audit logs
        stmt_audit = (
            select(AuditLog)
            .where(AuditLog.merchant_id == self.merchant_id)
            .order_by(AuditLog.created_at.desc())
            .limit(25)
        )
        self.audit_logs = list((await self.session.execute(stmt_audit)).scalars().all())

        return self
