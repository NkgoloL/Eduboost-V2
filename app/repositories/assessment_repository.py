"""Assessment persistence repository for EduBoost V2."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import text

from app.api.core.database import AsyncSessionFactory


class AssessmentRepository:
    async def list_assessments(self, limit: int = 50, offset: int = 0) -> list[dict]:
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                text(
                    "SELECT assessment_id, title, subject_code, grade_level, assessment_type, total_marks "
                    "FROM assessments WHERE is_active = TRUE ORDER BY grade_level, subject_code LIMIT :limit OFFSET :offset"
                ),
                {"limit": limit, "offset": offset},
            )
            return [dict(r) for r in result.mappings().all()]

    async def get_assessment(self, assessment_id: str):
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                text("SELECT assessment_id, total_marks, questions, passing_score FROM assessments WHERE assessment_id = :id AND is_active = TRUE"),
                {"id": assessment_id},
            )
            return result.mappings().first()

    async def create_attempt(self, assessment_id: str, learner_id: str, score: float, marks_obtained: int, time_taken_seconds: int, responses: list[dict]) -> str:
        attempt_id = str(uuid4())
        async with AsyncSessionFactory() as session:
            await session.execute(
                text(
                    "INSERT INTO assessment_attempts (attempt_id, learner_id, assessment_id, score, marks_obtained, time_taken_seconds, responses, completed_at) "
                    "VALUES (:attempt_id, :learner_id, :assessment_id, :score, :marks_obtained, :time_taken_seconds, :responses, :completed_at)"
                ),
                {
                    "attempt_id": attempt_id,
                    "learner_id": learner_id,
                    "assessment_id": assessment_id,
                    "score": score,
                    "marks_obtained": marks_obtained,
                    "time_taken_seconds": time_taken_seconds,
                    "responses": responses,
                    "completed_at": datetime.now(timezone.utc),
                },
            )
            await session.commit()
        return attempt_id
