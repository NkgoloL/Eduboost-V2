"""Lesson persistence repository for EduBoost V2."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import Lesson


class LessonRepository(BaseRepository[Lesson]):
    model = Lesson

    async def get_recent_for_learner(
        self,
        learner_id: UUID,
        db: AsyncSession,
        *,
        subject: str | None = None,
        limit: int = 10,
    ) -> list[Lesson]:
        stmt = (
            select(Lesson)
            .where(Lesson.learner_id == learner_id)
            .order_by(Lesson.created_at.desc())
            .limit(limit)
        )
        if subject:
            stmt = stmt.where(Lesson.subject == subject)
        result = await db.execute(stmt)
        return list(result.scalars().all())
