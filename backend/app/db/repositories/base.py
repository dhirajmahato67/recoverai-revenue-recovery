"""Generic asynchronous base repository providing tenant-scoped CRUD and pagination."""

import uuid
from typing import Any, Generic, TypeVar
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic async repository providing tenant-isolated data-access methods."""

    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model

    async def create(self, entity: T) -> T:
        """Add a new entity instance to the session and flush."""
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: uuid.UUID) -> T | None:
        """Retrieve an entity by primary key (unscoped)."""
        result = await self.session.execute(select(self.model).where(self.model.id == entity_id))
        return result.scalar_one_or_none()

    async def get_by_id_scoped(self, merchant_id: uuid.UUID, entity_id: uuid.UUID) -> T | None:
        """Retrieve an entity by primary key enforcing merchant tenancy."""
        stmt = select(self.model).where(
            self.model.id == entity_id,
            self.model.merchant_id == merchant_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_scoped(
        self,
        merchant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        order_by: Any = None,
    ) -> list[T]:
        """List tenant-scoped entities with pagination."""
        stmt = select(self.model).where(self.model.merchant_id == merchant_id)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        elif hasattr(self.model, "created_at"):
            stmt = stmt.order_by(self.model.created_at.desc())

        stmt = stmt.offset(skip).limit(min(limit, 100))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_scoped(self, merchant_id: uuid.UUID) -> int:
        """Count total tenant-scoped entities."""
        stmt = select(func.count()).select_from(self.model).where(self.model.merchant_id == merchant_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def paginate_scoped(
        self,
        merchant_id: uuid.UUID,
        page: int = 1,
        page_size: int = 50,
        order_by: Any = None,
    ) -> tuple[list[T], int]:
        """Paginate tenant-scoped entities and return (items, total_count)."""
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        skip = (page - 1) * page_size

        total = await self.count_scoped(merchant_id)
        items = await self.list_scoped(merchant_id, skip=skip, limit=page_size, order_by=order_by)
        return items, total
