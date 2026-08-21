"""Order repository for managing commerce purchase orders."""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.order import Order
from app.db.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Data-access methods for Order entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Order)

    async def get_by_external_id(self, merchant_id: uuid.UUID, external_order_id: str) -> Order | None:
        """Find an order by merchant-scoped external order ID."""
        stmt = select(Order).where(
            Order.merchant_id == merchant_id,
            Order.external_order_id == external_order_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
