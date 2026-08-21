"""RiskSignal domain model representing deterministic telemetry metrics supporting a risk case."""

import datetime
import uuid
from decimal import Decimal
from typing import Any, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, JSONType, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.risk_case import RiskCase


class RiskSignal(Base, UUIDPrimaryKeyMixin):
    """Deterministic telemetry metric / evidence datapoint supporting a RiskCase."""

    __tablename__ = "risk_signals"

    risk_case_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("risk_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)

    baseline_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    observed_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    deviation_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)

    dimension: Mapped[str | None] = mapped_column(String(100), nullable=True)  # payment_method, bank, etc.
    dimension_value: Mapped[str | None] = mapped_column(String(100), nullable=True)  # UPI, HDFC, etc.
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    risk_case: Mapped["RiskCase"] = relationship("RiskCase", back_populates="signals")

    __table_args__ = (
        Index("ix_risk_signals_case_metric", "risk_case_id", "metric_name"),
        Index("ix_risk_signals_case_type", "risk_case_id", "signal_type"),
    )
