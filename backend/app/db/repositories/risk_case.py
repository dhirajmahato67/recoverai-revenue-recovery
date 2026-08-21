"""RiskCase repository for revenue risk management."""

import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.risk_case import RiskCase
from app.db.repositories.base import BaseRepository


class RiskCaseRepository(BaseRepository[RiskCase]):
    """Data-access methods for RiskCase entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RiskCase)

    async def get_by_reference(self, merchant_id: uuid.UUID, case_reference: str) -> RiskCase | None:
        """Find a risk case by merchant-scoped reference (e.g. RC-001)."""
        stmt = select(RiskCase).where(
            RiskCase.merchant_id == merchant_id,
            RiskCase.case_reference == case_reference,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_details(self, merchant_id: uuid.UUID, risk_case_id: uuid.UUID) -> RiskCase | None:
        """Retrieve a risk case with its signals and investigations eagerly loaded."""
        stmt = (
            select(RiskCase)
            .where(
                RiskCase.id == risk_case_id,
                RiskCase.merchant_id == merchant_id,
            )
            .options(
                selectinload(RiskCase.signals),
                selectinload(RiskCase.investigations),
                selectinload(RiskCase.recovery_plans),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active_cases(self, merchant_id: uuid.UUID, limit: int = 50) -> list[RiskCase]:
        """List active/open risk cases for a merchant."""
        stmt = (
            select(RiskCase)
            .where(
                RiskCase.merchant_id == merchant_id,
                RiskCase.status.in_(["OPEN", "INVESTIGATING", "RECOMMENDED", "PENDING_APPROVAL", "RECOVERING"]),
            )
            .order_by(RiskCase.detected_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
