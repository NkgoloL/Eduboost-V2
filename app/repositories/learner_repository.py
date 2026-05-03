"""Learner persistence repository for EduBoost V2."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import Learner


class LearnerRepository(BaseRepository[Learner]):
    model = Learner

    async def get_by_id(self, learner_id: str | UUID, db: AsyncSession) -> Learner | None:
        return await self.get(UUID(str(learner_id)), db)

    async def delete_by_id(self, learner_id: str | UUID, db: AsyncSession) -> bool:
        """Physically delete a learner record (Right to Erasure)."""
        result = await db.execute(delete(Learner).where(Learner.id == UUID(str(learner_id))))
        return (result.rowcount or 0) > 0
