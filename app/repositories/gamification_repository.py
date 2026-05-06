"""Gamification persistence repository for EduBoost V2."""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import LearnerProfile


class GamificationRepository:
    def __init__(self, db: AsyncSession | None = None) -> None:
        self._db = db

    async def get_profile_rows(self, learner_id: str):
        async with _optional_session(self._db) as session:
            learner = await session.get(LearnerProfile, learner_id)
            if learner is None or learner.is_deleted:
                return None, []
            return learner, []

    async def get_leaderboard_rows(self, limit: int = 10):
        async with _optional_session(self._db) as session:
            result = await session.execute(
                select(LearnerProfile)
                .where(LearnerProfile.is_deleted == False)  # noqa: E712
                .order_by(desc(LearnerProfile.xp), desc(LearnerProfile.streak_days))
                .limit(limit)
            )
            return list(result.scalars().all())


class _optional_session:
    def __init__(self, db: AsyncSession | None) -> None:
        self.db = db
        self._owned = None

    async def __aenter__(self) -> AsyncSession:
        if self.db is not None:
            return self.db
        self._owned = AsyncSessionLocal()
        return await self._owned.__aenter__()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._owned is not None:
            await self._owned.__aexit__(exc_type, exc, tb)
