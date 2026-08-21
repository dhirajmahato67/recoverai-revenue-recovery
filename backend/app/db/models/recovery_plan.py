"""RecoveryPlan domain model representing bounded action policies for revenue recovery."""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.merchant import Merchant
    from app.db.models.risk_case import RiskCase
    from app.db.models.recovery_batch import RecoveryBatch
    from app.db.models.approval import Approval


class RecoveryPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Bounded recovery plan proposal outlining constraints before execution."""

    __tablename__ = "recovery_plans"

    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    risk_case_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("risk_cases.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)  # PAYMENT_RETRY, PAYMENT_METHOD_FALLBACK, CUSTOMER_RETRY, SIMULATED_RECOVERY
    estimated_recovery: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    maximum_exposure: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    failure_threshold: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.3000"), nullable=False)
    eligible_transaction_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False)  # DRAFT, PENDING_APPROVAL, APPROVED, REJECTED, EXECUTING, COMPLETED, STOPPED, FAILED, CANCELLED
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="recovery_plans")
    risk_case: Mapped["RiskCase"] = relationship("RiskCase", back_populates="recovery_plans")
    batches: Mapped[list["RecoveryBatch"]] = relationship("RecoveryBatch", back_populates="recovery_plan", lazy="selectin")
    approvals: Mapped[list["Approval"]] = relationship("Approval", back_populates="recovery_plan", lazy="selectin")

    __table_args__ = (
        CheckConstraint("estimated_recovery >= 0", name="chk_recovery_plans_estimated_positive"),
        CheckConstraint("maximum_exposure >= 0", name="chk_recovery_plans_exposure_positive"),
        CheckConstraint("max_retries >= 0", name="chk_recovery_plans_retries_positive"),
        CheckConstraint("failure_threshold >= 0 AND failure_threshold <= 1", name="chk_recovery_plans_threshold_range"),
        CheckConstraint("eligible_transaction_count >= 0", name="chk_recovery_plans_eligible_positive"),
        Index("ix_recovery_plans_merchant_status", "merchant_id", "status"),
    )
