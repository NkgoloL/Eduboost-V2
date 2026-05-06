"""Assessment persistence repository for EduBoost V2."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import Assessment, AssessmentAttempt


class AssessmentRepository(BaseRepository[Assessment]):
    model = Assessment

    async def list_active(
        self,
        db: AsyncSession,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Assessment]:
        """Return a list of active assessments."""
        return await self.list(db, filters={"is_active": True}, limit=limit, offset=offset)

    async def get_by_id_str(self, assessment_id: str, db: AsyncSession) -> Assessment | None:
        """Fetch a single assessment by its ID string."""
        return await self.get(UUID(assessment_id), db)


class AssessmentAttemptRepository(BaseRepository[AssessmentAttempt]):
    model = AssessmentAttempt

    async def create_attempt(
        self,
        db: AsyncSession,
        assessment_id: str | UUID,
        learner_id: str | UUID,
        score: float,
        marks_obtained: int,
        time_taken_seconds: int,
        responses: dict[str, Any],
    ) -> AssessmentAttempt:
        """Record a new assessment attempt."""
        return await self.create(
            db,
            assessment_id=UUID(str(assessment_id)),
            learner_id=UUID(str(learner_id)),
            score=score,
            marks_obtained=marks_obtained,
            time_taken_seconds=time_taken_seconds,
            responses=responses,
        )
