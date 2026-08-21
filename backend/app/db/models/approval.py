"""Approval domain model representing merchant admin authorization of recovery plans."""

import datetime
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.recovery_plan import RecoveryPlan


class Approval(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Explicit merchant authorization record required before executing financial workflows."""

    __tablename__ = "approvals"

    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    recovery_plan_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("recovery_plans.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    requested_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # PENDING, APPROVED, REJECTED, EXPIRED, CANCELLED
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    requested_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    approved_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    recovery_plan: Mapped["RecoveryPlan"] = relationship("RecoveryPlan", back_populates="approvals")

    __table_args__ = (
        Index("ix_approvals_merchant_status", "merchant_id", "status"),
    )
