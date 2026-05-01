"""Diagnostic persistence repository for EduBoost V2."""

from __future__ import annotations

import uuid

from sqlalchemy import insert

from app.api.core.database import AsyncSessionFactory
from app.api.models.db_models import DiagnosticSession as DiagnosticSessionRecord


class DiagnosticRepository:
    async def create_session(
        self,
        learner_id: str,
        subject_code: str,
        grade_level: int,
        theta: float,
        sem: float,
        items_administered: int,
        items_correct: int,
        items_total: int,
        final_mastery_score: float,
        knowledge_gaps: list,
    ) -> None:
        async with AsyncSessionFactory() as db:
            await db.execute(
                insert(DiagnosticSessionRecord).values(
                    session_id=uuid.uuid4(),
                    learner_id=uuid.UUID(learner_id),
                    subject_code=subject_code,
                    grade_level=grade_level,
                    status="completed",
                    theta_estimate=theta,
                    standard_error=sem,
                    items_administered=items_administered,
                    items_correct=items_correct,
                    items_total=items_total,
                    final_mastery_score=final_mastery_score,
                    knowledge_gaps=knowledge_gaps,
                )
            )
            await db.commit()
