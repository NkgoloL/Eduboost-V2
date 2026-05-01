"""Initial learner repository for V2 boundary enforcement."""

from __future__ import annotations

from sqlalchemy import select

from app.api.core.database import AsyncSessionFactory
from app.api.models.db_models import Learner
from app.domain.entities import LearnerProfile


class LearnerRepository:
    async def get_by_id(self, learner_id: str) -> LearnerProfile | None:
        async with AsyncSessionFactory() as session:
            result = await session.execute(select(Learner).where(Learner.learner_id == learner_id))
            learner = result.scalar_one_or_none()
            if learner is None:
                return None
            return LearnerProfile(
                learner_id=str(learner.learner_id),
                grade=learner.grade,
                home_language=learner.home_language,
                overall_mastery=learner.overall_mastery,
            )

    async def delete_by_id(self, learner_id: str) -> bool:
        """Physically delete a learner record (Right to Erasure)."""
        from sqlalchemy import delete
        async with AsyncSessionFactory() as session:
            result = await session.execute(delete(Learner).where(Learner.learner_id == learner_id))
            await session.commit()
            return result.rowcount > 0
