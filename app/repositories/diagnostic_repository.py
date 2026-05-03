"""Diagnostic persistence repository for EduBoost V2."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import DiagnosticSession


class DiagnosticRepository(BaseRepository[DiagnosticSession]):
    model = DiagnosticSession

    async def get_latest_for_learner(
        self,
        learner_id: UUID,
        subject: str,
        db: AsyncSession,
    ) -> DiagnosticSession | None:
        result = await db.execute(
            select(DiagnosticSession)
            .where(DiagnosticSession.learner_id == learner_id)
            .where(DiagnosticSession.subject == subject)
            .order_by(DiagnosticSession.started_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_session(
        self,
        learner_id: str | UUID,
        subject_code: str,
        grade_level: int | str,
        theta: float,
        sem: float,
        items_administered: int,
        items_correct: int,
        items_total: int,
        final_mastery_score: float,
        knowledge_gaps: list,
        db: AsyncSession,
    ) -> DiagnosticSession:
        return await self.create(
            db,
            learner_id=UUID(str(learner_id)),
            subject=subject_code,
            grade=str(grade_level),
            ability_estimate=theta,
            ability_std_error=sem,
            items_administered=items_administered,
            responses={
                "items_correct": items_correct,
                "items_total": items_total,
                "final_mastery_score": final_mastery_score,
                "knowledge_gaps": knowledge_gaps,
            },
            is_complete=True,
        )
