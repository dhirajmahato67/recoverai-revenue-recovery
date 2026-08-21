"""AuditLog domain model representing immutable fintech ledger events."""

import datetime
import uuid
from typing import Any, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, JSONType, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.merchant import Merchant


class AuditLog(Base, UUIDPrimaryKeyMixin):
    """Immutable audit trail record documenting financial, policy, AI, and administrative actions."""

    __tablename__ = "audit_logs"

    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)  # USER, AI_AGENT, POLICY_ENGINE, SYSTEM, RAZORPAY, WORKER
    actor_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # RISK_DETECTED, RECOVERY_RECOMMENDED, POLICY_VALIDATED, RECOVERY_APPROVED, RECOVERY_STARTED, RECOVERY_STOPPED, RECOVERY_COMPLETED, RECOVERY_FAILED
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)  # RiskCase, RecoveryPlan, RecoveryBatch, Payment, Policy
    resource_id: Mapped[str] = mapped_column(String(255), nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONType, default=dict, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_merchant_action", "merchant_id", "action"),
        Index("ix_audit_logs_merchant_resource", "merchant_id", "resource_type", "resource_id"),
        Index("ix_audit_logs_merchant_created_at", "merchant_id", "created_at"),
    )
