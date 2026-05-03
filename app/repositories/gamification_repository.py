"""Gamification persistence repository for EduBoost V2."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


class GamificationRepository:
    async def get_profile_rows(self, learner_id: str, db: AsyncSession | None = None):
        session_context = _optional_session(db)
        async with session_context as session:
            learner = await session.execute(
                text("SELECT * FROM learners WHERE id = :learner_id"),
                {"learner_id": learner_id},
            )
            learner_row = learner.mappings().first()
            if learner_row is None:
                return None, []
            return learner_row, []

    async def get_leaderboard_rows(self, limit: int = 10, db: AsyncSession | None = None):
        session_context = _optional_session(db)
        async with session_context as session:
            result = await session.execute(
                text("SELECT * FROM learners ORDER BY created_at DESC LIMIT :limit"),
                {"limit": limit},
            )
            return result.mappings().all()


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
