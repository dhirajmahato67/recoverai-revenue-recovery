"""PaymentEvent domain model representing raw inbound webhook and gateway events."""

import datetime
import uuid
from typing import Any, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, JSONType, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.payment import Payment


class PaymentEvent(Base, UUIDPrimaryKeyMixin):
    """Raw payment event / webhook message payload for telemetry and idempotent processing."""

    __tablename__ = "payment_events"

    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payment_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    signature_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="RECEIVED", nullable=False)  # RECEIVED, PROCESSING, PROCESSED, FAILED, IGNORED

    received_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    processed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    payment: Mapped["Payment | None"] = relationship("Payment", back_populates="events")

    __table_args__ = (
        Index("ix_payment_events_merchant_event_type", "merchant_id", "event_type"),
        Index("ix_payment_events_merchant_status", "merchant_id", "status"),
        Index("ix_payment_events_merchant_received_at", "merchant_id", "received_at"),
    )
