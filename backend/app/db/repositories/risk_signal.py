"""RiskSignal repository for managing deterministic telemetry metrics."""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.risk_signal import RiskSignal
from app.db.repositories.base import BaseRepository


class RiskSignalRepository(BaseRepository[RiskSignal]):
    """Data-access methods for RiskSignal telemetry datapoints."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RiskSignal)

    async def list_by_case(self, risk_case_id: uuid.UUID) -> list[RiskSignal]:
        """List all risk signals belonging to a given risk case."""
        stmt = (
            select(RiskSignal)
            .where(RiskSignal.risk_case_id == risk_case_id)
            .order_by(RiskSignal.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_recent_signals(self, merchant_id: uuid.UUID, limit: int = 50) -> list[RiskSignal]:
        """List recent risk signals across all cases for a merchant."""
        from app.db.models.risk_case import RiskCase

        stmt = (
            select(RiskSignal)
            .join(RiskCase, RiskSignal.risk_case_id == RiskCase.id)
            .where(RiskCase.merchant_id == merchant_id)
            .order_by(RiskSignal.created_at.desc())
            .limit(min(limit, 100))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
