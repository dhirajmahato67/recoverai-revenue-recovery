"""Customer repository for managing buyer profiles."""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.customer import Customer
from app.db.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    """Data-access methods for Customer entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Customer)

    async def get_by_external_id(self, merchant_id: uuid.UUID, external_customer_id: str) -> Customer | None:
        """Find a customer by merchant-scoped external customer ID."""
        stmt = select(Customer).where(
            Customer.merchant_id == merchant_id,
            Customer.external_customer_id == external_customer_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
