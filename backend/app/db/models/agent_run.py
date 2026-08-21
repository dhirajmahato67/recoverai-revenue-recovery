"""AgentRun domain model representing AI agent execution sessions."""

import datetime
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.risk_case import RiskCase
    from app.db.models.agent_tool_call import AgentToolCall


class AgentRun(Base, UUIDPrimaryKeyMixin):
    """AI agent diagnostic session record for observability and latency benchmarks."""

    __tablename__ = "agent_runs"

    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    risk_case_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("risk_cases.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    model: Mapped[str] = mapped_column(String(100), default="gemini-2.0-flash", nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), default="v1.0", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="STARTED", nullable=False)  # STARTED, COMPLETED, FAILED, CANCELLED

    started_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    risk_case: Mapped["RiskCase | None"] = relationship("RiskCase", back_populates="agent_runs")
    tool_calls: Mapped[list["AgentToolCall"]] = relationship("AgentToolCall", back_populates="agent_run", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("ix_agent_runs_merchant_status", "merchant_id", "status"),
    )
