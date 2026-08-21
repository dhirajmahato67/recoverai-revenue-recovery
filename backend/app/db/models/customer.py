"""Customer domain model representing consumer buyers."""

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.merchant import Merchant
    from app.db.models.order import Order
    from app.db.models.payment import Payment


class Customer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """End-customer / consumer account associated with a merchant."""

    __tablename__ = "customers"

    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    external_customer_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_last4: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="customers")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="customer")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="customer")

    __table_args__ = (
        UniqueConstraint("merchant_id", "external_customer_id", name="uq_customers_merchant_external_id"),
        Index("ix_customers_merchant_email", "merchant_id", "email"),
        Index("ix_customers_merchant_status", "merchant_id", "status"),
    )
