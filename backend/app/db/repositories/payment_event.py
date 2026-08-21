"""PaymentEvent repository for raw event deduplication and auditing."""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.payment_event import PaymentEvent
from app.db.repositories.base import BaseRepository


class PaymentEventRepository(BaseRepository[PaymentEvent]):
    """Data-access methods for raw PaymentEvent / Webhook telemetry."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PaymentEvent)

    async def get_by_event_id(self, event_id: str) -> PaymentEvent | None:
        """Find a payment event by unique event_id to prevent duplicate processing."""
        stmt = select(PaymentEvent).where(PaymentEvent.event_id == event_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
