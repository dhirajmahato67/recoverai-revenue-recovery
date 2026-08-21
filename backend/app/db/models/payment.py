"""Payment domain model representing payment attempts and settlements."""

import datetime
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.merchant import Merchant
    from app.db.models.order import Order
    from app.db.models.customer import Customer
    from app.db.models.payment_event import PaymentEvent
    from app.db.models.recovery_attempt import RecoveryAttempt


class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Payment transaction record processed through gateway."""

    __tablename__ = "payments"

    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    external_payment_id: Mapped[str] = mapped_column(String(255), nullable=False)

    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="CREATED", nullable=False)  # CREATED, AUTHORIZED, CAPTURED, FAILED, REFUNDED, CANCELLED
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)  # UPI, CARD, NETBANKING, WALLET, OTHER
    bank: Mapped[str | None] = mapped_column(String(100), nullable=True)  # HDFC, ICICI, SBI, AXIS, etc.

    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    captured_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="payments")
    order: Mapped["Order"] = relationship("Order", back_populates="payments")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="payments")
    events: Mapped[list["PaymentEvent"]] = relationship("PaymentEvent", back_populates="payment", lazy="selectin")
    recovery_attempts: Mapped[list["RecoveryAttempt"]] = relationship("RecoveryAttempt", back_populates="payment", lazy="selectin")

    __table_args__ = (
        CheckConstraint("amount >= 0", name="chk_payments_amount_positive"),
        UniqueConstraint("merchant_id", "external_payment_id", name="uq_payments_merchant_external_id"),
        Index("ix_payments_merchant_status", "merchant_id", "status"),
        Index("ix_payments_merchant_method", "merchant_id", "payment_method"),
        Index("ix_payments_merchant_bank", "merchant_id", "bank"),
        Index("ix_payments_merchant_created_at", "merchant_id", "created_at"),
    )
