"""Merchant repository for managing tenant registrations."""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.merchant import Merchant
from app.db.repositories.base import BaseRepository


class MerchantRepository(BaseRepository[Merchant]):
    """Data-access methods for Merchant entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Merchant)

    async def get_by_external_reference(self, external_reference: str) -> Merchant | None:
        """Find a merchant by external slug / reference."""
        stmt = select(Merchant).where(Merchant.external_reference == external_reference)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_merchants(self, limit: int = 50) -> list[Merchant]:
        """List active merchants on the platform."""
        stmt = select(Merchant).where(Merchant.status == "ACTIVE").limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
