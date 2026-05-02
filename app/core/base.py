"""
EduBoost SA — Base Repository
Generic async CRUD operations for all domain aggregates.
"""
from __future__ import annotations

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic repository providing standard async CRUD operations."""

    model: type[ModelT]

    async def get(self, id: UUID, db: AsyncSession) -> ModelT | None:
        result = await db.execute(select(self.model).where(self.model.id == id))  # type: ignore[attr-defined]
        return result.scalar_one_or_none()

    async def get_or_404(self, id: UUID, db: AsyncSession) -> ModelT:
        from app.core.exceptions import NotFoundError
        instance = await self.get(id, db)
        if instance is None:
            raise NotFoundError(f"{self.model.__name__} {id} not found")
        return instance

    async def list(
        self,
        db: AsyncSession,
        *,
        filters: dict[str, Any] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ModelT]:
        stmt = select(self.model)
        if filters:
            for field, value in filters.items():
                stmt = stmt.where(getattr(self.model, field) == value)
        stmt = stmt.limit(limit).offset(offset)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, **kwargs: Any) -> ModelT:
        instance = self.model(**kwargs)
        db.add(instance)
        await db.flush()  # Get the ID without committing
        await db.refresh(instance)
        return instance

    async def update(self, instance: ModelT, db: AsyncSession, **kwargs: Any) -> ModelT:
        for field, value in kwargs.items():
            setattr(instance, field, value)
        db.add(instance)
        await db.flush()
        await db.refresh(instance)
        return instance

    async def delete(self, instance: ModelT, db: AsyncSession) -> None:
        await db.delete(instance)
        await db.flush()
