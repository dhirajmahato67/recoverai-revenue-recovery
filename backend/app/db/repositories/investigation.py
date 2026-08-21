"""Investigation repository for diagnostic investigations."""

import uuid
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.investigation import Investigation
from app.db.models.risk_case import RiskCase
from app.db.repositories.base import BaseRepository


class InvestigationRepository(BaseRepository[Investigation]):
    """Data-access methods for Investigation entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Investigation)

    async def get_for_case(self, risk_case_id: uuid.UUID) -> list[Investigation]:
        """List investigations associated with a risk case."""
        stmt = (
            select(Investigation)
            .where(Investigation.risk_case_id == risk_case_id)
            .order_by(Investigation.started_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_for_case(
        self, merchant_id: uuid.UUID, risk_case_id: uuid.UUID
    ) -> Investigation | None:
        """Get latest investigation for a specific risk case owned by merchant."""
        stmt = (
            select(Investigation)
            .join(RiskCase, Investigation.risk_case_id == RiskCase.id)
            .where(
                RiskCase.merchant_id == merchant_id,
                Investigation.risk_case_id == risk_case_id,
            )
            .options(
                selectinload(Investigation.risk_case).selectinload(RiskCase.signals),
            )
            .order_by(Investigation.started_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_id_scoped(
        self, merchant_id: uuid.UUID, investigation_id: uuid.UUID
    ) -> Investigation | None:
        """Retrieve investigation by ID with tenant scope check and eager relationships."""
        stmt = (
            select(Investigation)
            .join(RiskCase, Investigation.risk_case_id == RiskCase.id)
            .where(
                RiskCase.merchant_id == merchant_id,
                Investigation.id == investigation_id,
            )
            .options(
                selectinload(Investigation.risk_case).selectinload(RiskCase.signals),
                selectinload(Investigation.risk_case).selectinload(RiskCase.investigations),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_merchant(
        self, merchant_id: uuid.UUID, limit: int = 50, skip: int = 0
    ) -> list[Investigation]:
        """List investigations for a merchant with pagination."""
        stmt = (
            select(Investigation)
            .join(RiskCase, Investigation.risk_case_id == RiskCase.id)
            .where(RiskCase.merchant_id == merchant_id)
            .options(
                selectinload(Investigation.risk_case),
            )
            .order_by(Investigation.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_for_merchant(self, merchant_id: uuid.UUID) -> int:
        """Count total investigations for a merchant."""
        stmt = (
            select(func.count(Investigation.id))
            .join(RiskCase, Investigation.risk_case_id == RiskCase.id)
            .where(RiskCase.merchant_id == merchant_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0
