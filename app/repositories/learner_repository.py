"""Learner persistence repository for EduBoost V2."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import Learner


class LearnerRepository(BaseRepository[Learner]):
    model = Learner

    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db

    def _db(self, db: AsyncSession | None) -> AsyncSession:
        session = db or self.db
        if session is None:
            raise ValueError("LearnerRepository requires an AsyncSession")
        return session

    async def get_by_id(self, learner_id: str | UUID, db: AsyncSession | None = None) -> Learner | None:
        db = self._db(db)
        return await self.get(UUID(str(learner_id)), db)

    async def delete_by_id(self, learner_id: str | UUID, db: AsyncSession | None = None) -> bool:
        """Physically delete a learner record (Right to Erasure)."""
        db = self._db(db)
        result = await db.execute(delete(Learner).where(Learner.id == UUID(str(learner_id))))
        return (result.rowcount or 0) > 0

    async def soft_delete(self, learner_id: str | UUID, db: AsyncSession | None = None) -> None:
        db = self._db(db)
        learner = await self.get_by_id(learner_id, db)
        if learner is None:
            return
        learner.display_name = "[erased]"
        learner.is_deleted = True
        learner.deletion_requested_at = datetime.now(UTC)
        db.add(learner)
        await db.flush()

    async def purge_personal_data(self, learner_id: str | UUID, db: AsyncSession | None = None) -> None:
        db = self._db(db)
        await db.execute(delete(Learner).where(Learner.id == UUID(str(learner_id))))
