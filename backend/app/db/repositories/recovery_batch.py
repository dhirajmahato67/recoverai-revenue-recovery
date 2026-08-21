"""RecoveryBatch repository for batch dispatch and execution tracking."""

import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.recovery_batch import RecoveryBatch
from app.db.repositories.base import BaseRepository


class RecoveryBatchRepository(BaseRepository[RecoveryBatch]):
    """Data-access methods for RecoveryBatch entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RecoveryBatch)

    async def get_by_reference(self, merchant_id: uuid.UUID, batch_reference: str) -> RecoveryBatch | None:
        """Find a recovery batch by merchant-scoped reference (e.g. RB-001)."""
        stmt = select(RecoveryBatch).where(
            RecoveryBatch.merchant_id == merchant_id,
            RecoveryBatch.batch_reference == batch_reference,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, idempotency_key: str) -> RecoveryBatch | None:
        """Find a batch by unique idempotency key to prevent double execution."""
        stmt = select(RecoveryBatch).where(RecoveryBatch.idempotency_key == idempotency_key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_attempts(self, merchant_id: uuid.UUID, batch_id: uuid.UUID) -> RecoveryBatch | None:
        """Retrieve a recovery batch with all transaction attempt records loaded."""
        stmt = (
            select(RecoveryBatch)
            .where(
                RecoveryBatch.id == batch_id,
                RecoveryBatch.merchant_id == merchant_id,
            )
            .options(selectinload(RecoveryBatch.attempts))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
