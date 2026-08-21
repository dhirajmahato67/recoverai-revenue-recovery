"""FastAPI router for Audit Trail ledger records."""

import hashlib
import json
import uuid
from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditLog
from app.db.session import get_db

router = APIRouter(prefix="", tags=["Audit"])


class AuditEventResponse(BaseModel):
    """Audit log item formatted for frontend UI."""

    id: str
    timestamp: str
    timeDisplay: str
    actorType: str
    actorName: str
    action: str
    targetType: str
    targetId: str
    targetDisplay: str
    result: str
    summary: str
    cryptographicHash: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="ignore")


@router.get(
    "/audit",
    response_model=list[AuditEventResponse],
    summary="List Audit Logs",
)
@router.get(
    "/audit/logs",
    response_model=list[AuditEventResponse],
    summary="List Audit Logs (Nested)",
    include_in_schema=False,
)
@router.get(
    "/audit-logs",
    response_model=list[AuditEventResponse],
    summary="List Audit Logs (Alias)",
    include_in_schema=False,
)
async def list_audit_logs(
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    actorType: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[AuditEventResponse]:
    """Retrieve immutable audit trail entries."""
    stmt = (
        select(AuditLog)
        .where(AuditLog.merchant_id == merchant_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )

    if actorType and actorType != "ALL":
        stmt = stmt.where(AuditLog.actor_type == actorType)

    result = await db.execute(stmt)
    logs = list(result.scalars().all())

    events: list[AuditEventResponse] = []
    for log in logs:
        ts_str = log.created_at.isoformat() if log.created_at else ""
        time_display = log.created_at.strftime("%I:%M %p") if log.created_at else ""

        # Deterministic SHA-256 hash
        hash_input = f"{log.id}-{log.created_at}-{log.action}-{log.resource_type}-{log.resource_id}"
        crypto_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:32]

        summary_text = (
            f"{log.actor_type} performed {log.action.replace('_', ' ').title()} on {log.resource_type} {log.resource_id}."
        )

        events.append(
            AuditEventResponse(
                id=f"AUD-{str(log.id)[:8].upper()}",
                timestamp=ts_str,
                timeDisplay=time_display,
                actorType=log.actor_type,
                actorName=log.actor_id or log.actor_type.title(),
                action=log.action,
                targetType="RISK_CASE" if log.resource_type == "RiskCase" else ("TRANSACTION" if log.resource_type == "Payment" else "SYSTEM"),
                targetId=log.resource_id,
                targetDisplay=f"{log.resource_type} {log.resource_id}",
                result="SUCCESS",
                summary=summary_text,
                cryptographicHash=crypto_hash,
                metadata=log.metadata_ or {},
            )
        )

    return events
