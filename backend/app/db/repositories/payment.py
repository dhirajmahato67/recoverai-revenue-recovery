"""Payment repository for managing transactions and telemetry queries."""

import datetime
import uuid
from decimal import Decimal
from typing import Any
from sqlalchemy import func, select, and_, case
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.payment import Payment
from app.db.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Data-access methods for Payment transactions."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Payment)

    async def get_by_external_id(self, merchant_id: uuid.UUID, external_payment_id: str) -> Payment | None:
        """Find a payment by merchant-scoped external payment ID."""
        stmt = select(Payment).where(
            Payment.merchant_id == merchant_id,
            Payment.external_payment_id == external_payment_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_external_ids(self, merchant_id: uuid.UUID, external_ids: list[str]) -> set[str]:
        """Find which external payment IDs already exist for the merchant."""
        if not external_ids:
            return set()
        stmt = select(Payment.external_payment_id).where(
            Payment.merchant_id == merchant_id,
            Payment.external_payment_id.in_(external_ids),
        )
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    async def list_payments_filtered(
        self,
        merchant_id: uuid.UUID,
        status: str | None = None,
        payment_method: str | None = None,
        bank: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Payment]:
        """List tenant-scoped payments filtered by status, method, bank, or search query."""
        stmt = (
            select(Payment)
            .where(Payment.merchant_id == merchant_id)
            .options(
                selectinload(Payment.order),
                selectinload(Payment.customer),
                selectinload(Payment.events),
            )
        )
        if status:
            stmt = stmt.where(Payment.status == status)
        if payment_method:
            stmt = stmt.where(Payment.payment_method == payment_method)
        if bank:
            stmt = stmt.where(Payment.bank == bank)
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                Payment.external_payment_id.ilike(search_pattern)
                | Payment.bank.ilike(search_pattern)
                | Payment.error_code.ilike(search_pattern)
            )

        stmt = stmt.order_by(Payment.created_at.desc()).offset(skip).limit(min(limit, 100))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_payments_filtered(
        self,
        merchant_id: uuid.UUID,
        status: str | None = None,
        payment_method: str | None = None,
        bank: str | None = None,
        search: str | None = None,
    ) -> int:
        """Count tenant-scoped payments matching filters."""
        stmt = select(func.count()).select_from(Payment).where(Payment.merchant_id == merchant_id)
        if status:
            stmt = stmt.where(Payment.status == status)
        if payment_method:
            stmt = stmt.where(Payment.payment_method == payment_method)
        if bank:
            stmt = stmt.where(Payment.bank == bank)
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                Payment.external_payment_id.ilike(search_pattern)
                | Payment.bank.ilike(search_pattern)
                | Payment.error_code.ilike(search_pattern)
            )

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_window_summary(
        self,
        merchant_id: uuid.UUID,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
    ) -> dict[str, Any]:
        """Aggregate total count, captured count, failed count, and financial volumes in a time window."""
        stmt = select(
            func.count(Payment.id).label("total_count"),
            func.count(case((Payment.status == "CAPTURED", Payment.id))).label("captured_count"),
            func.count(case((Payment.status == "FAILED", Payment.id))).label("failed_count"),
            func.coalesce(func.sum(Payment.amount), Decimal("0.00")).label("total_amount"),
            func.coalesce(
                func.sum(case((Payment.status == "FAILED", Payment.amount), else_=Decimal("0.00"))),
                Decimal("0.00"),
            ).label("failed_amount"),
        ).where(
            Payment.merchant_id == merchant_id,
            Payment.created_at >= start_time,
            Payment.created_at <= end_time,
        )

        result = await self.session.execute(stmt)
        row = result.one()
        total = row.total_count or 0
        captured = row.captured_count or 0
        failed = row.failed_count or 0
        success_rate = (captured / total) if total > 0 else 0.0

        return {
            "total_count": total,
            "captured_count": captured,
            "failed_count": failed,
            "success_rate": success_rate,
            "total_amount": row.total_amount,
            "failed_amount": row.failed_amount,
        }

    async def get_window_method_breakdown(
        self,
        merchant_id: uuid.UUID,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
    ) -> dict[str, dict[str, Any]]:
        """Calculate success rates and volumes broken down by payment method."""
        stmt = (
            select(
                Payment.payment_method,
                func.count(Payment.id).label("total_count"),
                func.count(case((Payment.status == "CAPTURED", Payment.id))).label("captured_count"),
                func.count(case((Payment.status == "FAILED", Payment.id))).label("failed_count"),
                func.coalesce(func.sum(Payment.amount), Decimal("0.00")).label("total_amount"),
                func.coalesce(
                    func.sum(case((Payment.status == "FAILED", Payment.amount), else_=Decimal("0.00"))),
                    Decimal("0.00"),
                ).label("failed_amount"),
            )
            .where(
                Payment.merchant_id == merchant_id,
                Payment.created_at >= start_time,
                Payment.created_at <= end_time,
            )
            .group_by(Payment.payment_method)
        )

        result = await self.session.execute(stmt)
        breakdown = {}
        for row in result.all():
            total = row.total_count or 0
            captured = row.captured_count or 0
            rate = (captured / total) if total > 0 else 0.0
            breakdown[row.payment_method] = {
                "total_count": total,
                "captured_count": captured,
                "failed_count": row.failed_count or 0,
                "success_rate": rate,
                "total_amount": row.total_amount,
                "failed_amount": row.failed_amount,
            }
        return breakdown

    async def get_window_bank_breakdown(
        self,
        merchant_id: uuid.UUID,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
    ) -> dict[str, dict[str, Any]]:
        """Calculate success rates and volumes broken down by issuing bank."""
        stmt = (
            select(
                Payment.bank,
                func.count(Payment.id).label("total_count"),
                func.count(case((Payment.status == "CAPTURED", Payment.id))).label("captured_count"),
                func.count(case((Payment.status == "FAILED", Payment.id))).label("failed_count"),
                func.coalesce(
                    func.sum(case((Payment.status == "FAILED", Payment.amount), else_=Decimal("0.00"))),
                    Decimal("0.00"),
                ).label("failed_amount"),
            )
            .where(
                Payment.merchant_id == merchant_id,
                Payment.created_at >= start_time,
                Payment.created_at <= end_time,
            )
            .group_by(Payment.bank)
        )

        result = await self.session.execute(stmt)
        breakdown = {}
        for row in result.all():
            bank_name = row.bank or "OTHER"
            total = row.total_count or 0
            captured = row.captured_count or 0
            rate = (captured / total) if total > 0 else 0.0
            breakdown[bank_name] = {
                "total_count": total,
                "captured_count": captured,
                "failed_count": row.failed_count or 0,
                "success_rate": rate,
                "failed_amount": row.failed_amount,
            }
        return breakdown

    async def get_window_error_breakdown(
        self,
        merchant_id: uuid.UUID,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
    ) -> dict[str, int]:
        """Aggregate counts for each error code in a time window."""
        stmt = (
            select(
                Payment.error_code,
                func.count(Payment.id).label("error_count"),
            )
            .where(
                Payment.merchant_id == merchant_id,
                Payment.status == "FAILED",
                Payment.created_at >= start_time,
                Payment.created_at <= end_time,
                Payment.error_code.isnot(None),
            )
            .group_by(Payment.error_code)
        )

        result = await self.session.execute(stmt)
        return {row.error_code: row.error_count for row in result.all()}

    async def get_merchant_transaction_bounds(
        self,
        merchant_id: uuid.UUID,
    ) -> tuple[datetime.datetime | None, datetime.datetime | None]:
        """Fetch earliest and latest transaction timestamps for tenant investigation scoping."""
        stmt = select(
            func.min(Payment.created_at),
            func.max(Payment.created_at),
        ).where(Payment.merchant_id == merchant_id)
        result = await self.session.execute(stmt)
        min_created, max_created = result.one()
        return min_created, max_created

    async def get_window_method_bank_breakdown(
        self,
        merchant_id: uuid.UUID,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
    ) -> list[dict[str, Any]]:
        """Calculate breakdown segmented by payment method, bank, and error code."""
        stmt = (
            select(
                Payment.payment_method,
                Payment.bank,
                Payment.error_code,
                func.count(Payment.id).label("total_count"),
                func.count(case((Payment.status == "CAPTURED", Payment.id))).label("captured_count"),
                func.count(case((Payment.status == "FAILED", Payment.id))).label("failed_count"),
            )
            .where(
                Payment.merchant_id == merchant_id,
                Payment.created_at >= start_time,
                Payment.created_at <= end_time,
            )
            .group_by(Payment.payment_method, Payment.bank, Payment.error_code)
        )
        result = await self.session.execute(stmt)
        return [
            {
                "payment_method": row.payment_method,
                "bank": row.bank or "OTHER",
                "error_code": row.error_code,
                "total_count": row.total_count or 0,
                "captured_count": row.captured_count or 0,
                "failed_count": row.failed_count or 0,
            }
            for row in result.all()
        ]

