"""RiskCase domain model representing detected revenue leakage incidents."""

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
    Text,
    UniqueConstraint,
    func,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.merchant import Merchant
    from app.db.models.risk_signal import RiskSignal
    from app.db.models.investigation import Investigation
    from app.db.models.recovery_plan import RecoveryPlan
    from app.db.models.agent_run import AgentRun


class RiskCase(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Incident record for detected payment or revenue degradation."""

    __tablename__ = "risk_cases"

    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    case_reference: Mapped[str] = mapped_column(String(50), nullable=False)  # RC-001, etc.
    risk_type: Mapped[str] = mapped_column(String(100), nullable=False)  # PAYMENT_DEGRADATION, CHECKOUT_ABANDONMENT, etc.
    severity: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False)  # OPEN, INVESTIGATING, RECOMMENDED, PENDING_APPROVAL, RECOVERING, RESOLVED, CLOSED, DISMISSED
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    revenue_at_risk: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    estimated_recoverable_revenue: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.9000"), nullable=False)

    detected_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    resolved_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="risk_cases")
    signals: Mapped[list["RiskSignal"]] = relationship("RiskSignal", back_populates="risk_case", cascade="all, delete-orphan", lazy="selectin")
    investigations: Mapped[list["Investigation"]] = relationship("Investigation", back_populates="risk_case", cascade="all, delete-orphan", lazy="selectin")
    recovery_plans: Mapped[list["RecoveryPlan"]] = relationship("RecoveryPlan", back_populates="risk_case", lazy="selectin")
    agent_runs: Mapped[list["AgentRun"]] = relationship("AgentRun", back_populates="risk_case", lazy="selectin")

    __table_args__ = (
        CheckConstraint("revenue_at_risk >= 0", name="chk_risk_cases_revenue_at_risk_positive"),
        CheckConstraint("estimated_recoverable_revenue >= 0", name="chk_risk_cases_recoverable_positive"),
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 1", name="chk_risk_cases_confidence_range"),
        UniqueConstraint("merchant_id", "case_reference", name="uq_risk_cases_merchant_reference"),
        Index("ix_risk_cases_merchant_type", "merchant_id", "risk_type"),
        Index("ix_risk_cases_merchant_severity", "merchant_id", "severity"),
        Index("ix_risk_cases_merchant_status", "merchant_id", "status"),
        Index("ix_risk_cases_merchant_detected_at", "merchant_id", "detected_at"),
    )
