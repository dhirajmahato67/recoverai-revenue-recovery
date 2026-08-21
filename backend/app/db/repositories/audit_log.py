"""AuditLog repository for immutable fintech ledger recording and querying."""

import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.audit_log import AuditLog
from app.db.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Data-access methods for AuditLog records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuditLog)

    async def record_event(
        self,
        merchant_id: uuid.UUID,
        actor_type: str,
        action: str,
        resource_type: str,
        resource_id: str,
        actor_id: str | None = None,
        request_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Create and flush an immutable audit trail entry."""
        log_entry = AuditLog(
            merchant_id=merchant_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            request_id=request_id,
            metadata_=metadata or {},
        )
        self.session.add(log_entry)
        await self.session.flush()
        return log_entry

    async def list_for_resource(
        self,
        merchant_id: uuid.UUID,
        resource_type: str,
        resource_id: str,
        limit: int = 50,
    ) -> list[AuditLog]:
        """List audit events specifically tied to a given entity."""
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.merchant_id == merchant_id,
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
