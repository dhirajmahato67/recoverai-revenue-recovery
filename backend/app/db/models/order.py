"""Order domain model representing purchase orders."""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.merchant import Merchant
    from app.db.models.customer import Customer
    from app.db.models.payment import Payment


class Order(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Commerce purchase order placed by a customer."""

    __tablename__ = "orders"

    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    external_order_id: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="CREATED", nullable=False)  # CREATED, ATTEMPTED, PAID, FAILED, CANCELLED
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="orders")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="order", lazy="selectin")

    __table_args__ = (
        CheckConstraint("amount >= 0", name="chk_orders_amount_positive"),
        UniqueConstraint("merchant_id", "external_order_id", name="uq_orders_merchant_external_id"),
        Index("ix_orders_merchant_status", "merchant_id", "status"),
        Index("ix_orders_merchant_created_at", "merchant_id", "created_at"),
    )
