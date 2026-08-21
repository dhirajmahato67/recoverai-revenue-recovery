"""RecoveryPlan repository for recovery policies and proposals."""

import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.recovery_plan import RecoveryPlan
from app.db.repositories.base import BaseRepository


class RecoveryPlanRepository(BaseRepository[RecoveryPlan]):
    """Data-access methods for RecoveryPlan entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RecoveryPlan)

    async def get_with_batches_and_approvals(
        self, merchant_id: uuid.UUID, recovery_plan_id: uuid.UUID
    ) -> RecoveryPlan | None:
        """Retrieve a recovery plan with associated batches and approvals loaded."""
        stmt = (
            select(RecoveryPlan)
            .where(
                RecoveryPlan.id == recovery_plan_id,
                RecoveryPlan.merchant_id == merchant_id,
            )
            .options(
                selectinload(RecoveryPlan.batches),
                selectinload(RecoveryPlan.approvals),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
