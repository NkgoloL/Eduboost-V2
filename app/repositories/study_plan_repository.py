"""Study plan persistence repository for EduBoost V2."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import StudyPlan


class StudyPlanRepository(BaseRepository[StudyPlan]):
    model = StudyPlan

    async def list_for_learner(
        self,
        learner_id: str | UUID,
        db: AsyncSession,
        *,
        limit: int = 10,
    ) -> list[StudyPlan]:
        """Return the N most recent study plans for a learner."""
        stmt = (
            select(StudyPlan)
            .where(StudyPlan.learner_id == UUID(str(learner_id)))
            .order_by(StudyPlan.week_start.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_for_learner(
        self,
        learner_id: str | UUID,
        db: AsyncSession,
    ) -> StudyPlan | None:
        """Fetch the most recent study plan for a learner."""
        plans = await self.list_for_learner(learner_id, db, limit=1)
        return plans[0] if plans else None
