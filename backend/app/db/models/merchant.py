"""Merchant domain model representing registered business entities."""

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.customer import Customer
    from app.db.models.order import Order
    from app.db.models.payment import Payment
    from app.db.models.risk_case import RiskCase
    from app.db.models.recovery_plan import RecoveryPlan
    from app.db.models.audit_log import AuditLog


class Merchant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Registered corporate merchant on the RecoverAI platform."""

    __tablename__ = "merchants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, SUSPENDED, INACTIVE
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="merchant", cascade="all, delete-orphan", lazy="selectin")
    customers: Mapped[list["Customer"]] = relationship("Customer", back_populates="merchant", lazy="selectin")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="merchant", lazy="selectin")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="merchant", lazy="selectin")
    risk_cases: Mapped[list["RiskCase"]] = relationship("RiskCase", back_populates="merchant", lazy="selectin")
    recovery_plans: Mapped[list["RecoveryPlan"]] = relationship("RecoveryPlan", back_populates="merchant", lazy="selectin")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="merchant", lazy="selectin")

    __table_args__ = (
        Index("ix_merchants_status", "status"),
    )
