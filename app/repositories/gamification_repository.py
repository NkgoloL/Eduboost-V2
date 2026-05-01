"""Gamification persistence repository for EduBoost V2."""

from __future__ import annotations

from sqlalchemy import select

from app.api.core.database import AsyncSessionFactory
from app.api.models.db_models import Learner, LearnerBadge, Badge


class GamificationRepository:
    async def get_profile_rows(self, learner_id: str):
        async with AsyncSessionFactory() as session:
            learner = await session.get(Learner, learner_id)
            if learner is None:
                return None, []
            result = await session.execute(
                select(LearnerBadge, Badge)
                .join(Badge, LearnerBadge.badge_id == Badge.badge_id)
                .where(LearnerBadge.learner_id == learner_id)
            )
            return learner, result.all()

    async def get_leaderboard_rows(self, limit: int = 10):
        async with AsyncSessionFactory() as session:
            result = await session.execute(select(Learner).order_by(Learner.total_xp.desc()).limit(limit))
            return result.scalars().all()
