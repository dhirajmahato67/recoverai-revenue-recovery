"""User domain model for merchant team members and roles."""

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.merchant import Merchant


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Team member associated with a merchant tenant."""

    __tablename__ = "users"

    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="MERCHANT", nullable=False)  # ADMIN, MERCHANT, ANALYST, VIEWER
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, SUSPENDED, INVITED

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="users")

    __table_args__ = (
        UniqueConstraint("merchant_id", "email", name="uq_users_merchant_email"),
        Index("ix_users_merchant_role", "merchant_id", "role"),
        Index("ix_users_merchant_status", "merchant_id", "status"),
    )
