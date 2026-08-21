"""Investigation domain model representing structured diagnostic analysis of risk cases."""

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
    func,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.risk_case import RiskCase


class Investigation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Structured diagnostic investigation record evaluating root causes and findings."""

    __tablename__ = "investigations"

    risk_case_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("risk_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # PENDING, RUNNING, COMPLETED, FAILED
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.9000"), nullable=False)

    started_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    risk_case: Mapped["RiskCase"] = relationship("RiskCase", back_populates="investigations")

    __table_args__ = (
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 1", name="chk_investigations_confidence_range"),
        Index("ix_investigations_case_status", "risk_case_id", "status"),
    )
