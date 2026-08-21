"""AgentToolCall domain model representing technical sub-agent tool execution logs."""

import datetime
import uuid
from typing import Any, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, JSONType, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.agent_run import AgentRun


class AgentToolCall(Base, UUIDPrimaryKeyMixin):
    """Execution record for an individual diagnostic tool invoked during an AgentRun."""

    __tablename__ = "agent_tool_calls"

    agent_run_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)  # get_case_details, get_root_cause, calculate_recovery_estimate, etc.
    arguments: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    result: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="STARTED", nullable=False)  # STARTED, COMPLETED, FAILED
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    agent_run: Mapped["AgentRun"] = relationship("AgentRun", back_populates="tool_calls")

    __table_args__ = (
        Index("ix_agent_tool_calls_run_tool", "agent_run_id", "tool_name"),
    )
