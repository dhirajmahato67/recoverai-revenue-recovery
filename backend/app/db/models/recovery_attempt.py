"""RecoveryAttempt domain model representing individual transaction retry actions."""

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
    func,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.recovery_batch import RecoveryBatch
    from app.db.models.payment import Payment


class RecoveryAttempt(Base, UUIDPrimaryKeyMixin):
    """Individual retry attempt executed for a specific failed payment transaction."""

    __tablename__ = "recovery_attempts"

    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    recovery_batch_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("recovery_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payment_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("payments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # PENDING, PROCESSING, SUCCESS, FAILED, SKIPPED, STOPPED
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    executed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    recovery_batch: Mapped["RecoveryBatch"] = relationship("RecoveryBatch", back_populates="attempts")
    payment: Mapped["Payment"] = relationship("Payment", back_populates="recovery_attempts")

    __table_args__ = (
        CheckConstraint("attempt_number > 0", name="chk_recovery_attempts_number_positive"),
        CheckConstraint("amount >= 0", name="chk_recovery_attempts_amount_positive"),
        UniqueConstraint("recovery_batch_id", "payment_id", "attempt_number", name="uq_recovery_attempts_batch_payment_attempt"),
        Index("ix_recovery_attempts_merchant_status", "merchant_id", "status"),
    )
