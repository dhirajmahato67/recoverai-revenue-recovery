"""RecoveryBatch domain model representing execution batches of recovery workflows."""

import datetime
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.recovery_plan import RecoveryPlan
    from app.db.models.recovery_attempt import RecoveryAttempt


class RecoveryBatch(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Execution batch tracking grouped recovery attempts with idempotency protection."""

    __tablename__ = "recovery_batches"

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
    batch_reference: Mapped[str] = mapped_column(String(50), nullable=False)  # RB-001, RB-024, etc.
    status: Mapped[str] = mapped_column(String(50), default="CREATED", nullable=False)  # CREATED, PENDING_APPROVAL, APPROVED, EXECUTING, COMPLETED, PARTIALLY_COMPLETED, STOPPED, FAILED, CANCELLED

    total_transactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    eligible_transactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    attempted_transactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_transactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_transactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_transactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    estimated_recovery: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    actual_recovery: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)

    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    started_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    recovery_plan: Mapped["RecoveryPlan"] = relationship("RecoveryPlan", back_populates="batches")
    attempts: Mapped[list["RecoveryAttempt"]] = relationship("RecoveryAttempt", back_populates="recovery_batch", lazy="selectin")

    __table_args__ = (
        CheckConstraint("total_transactions >= 0", name="chk_recovery_batches_total_positive"),
        CheckConstraint("eligible_transactions >= 0", name="chk_recovery_batches_eligible_positive"),
        CheckConstraint("attempted_transactions >= 0", name="chk_recovery_batches_attempted_positive"),
        CheckConstraint("successful_transactions >= 0", name="chk_recovery_batches_successful_positive"),
        CheckConstraint("failed_transactions >= 0", name="chk_recovery_batches_failed_positive"),
        CheckConstraint("skipped_transactions >= 0", name="chk_recovery_batches_skipped_positive"),
        CheckConstraint("estimated_recovery >= 0", name="chk_recovery_batches_estimated_positive"),
        CheckConstraint("actual_recovery >= 0", name="chk_recovery_batches_actual_positive"),
        UniqueConstraint("merchant_id", "batch_reference", name="uq_recovery_batches_merchant_reference"),
        Index("ix_recovery_batches_merchant_status", "merchant_id", "status"),
        Index("ix_recovery_batches_merchant_created_at", "merchant_id", "created_at"),
    )
