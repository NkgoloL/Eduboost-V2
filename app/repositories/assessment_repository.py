"""Assessment persistence repository for EduBoost V2."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import Assessment, AssessmentAttempt


class AssessmentRepository(BaseRepository[Assessment]):
    """Canonical assessment repository with live-route compatibility methods."""

    model = Assessment

    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db

    def _resolve_db(self, db: AsyncSession | None = None) -> AsyncSession:
        session = db or self.db
        if session is None:
            raise ValueError("AssessmentRepository requires an AsyncSession")
        return session

    async def list_active(
        self,
        db: AsyncSession | None = None,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Assessment]:
        """Return a list of active assessments."""
        return await self.list(self._resolve_db(db), filters={"is_active": True}, limit=limit, offset=offset)

    async def get_by_id_str(self, assessment_id: str, db: AsyncSession | None = None) -> Assessment | None:
        """Fetch a single assessment by its ID string."""
        return await self.get(UUID(str(assessment_id)), self._resolve_db(db))

    async def list_assessments(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        db: AsyncSession | None = None,
    ) -> list[dict[str, Any]]:
        """Compatibility method consumed by AssessmentServiceV2 live routes."""
        rows = await self.list_active(db, limit=limit, offset=offset)
        return [self.to_payload(row) for row in rows]

    async def get_assessment(
        self,
        assessment_id: str,
        db: AsyncSession | None = None,
    ) -> dict[str, Any] | None:
        """Compatibility method consumed by AssessmentServiceV2 live routes."""
        row = await self.get_by_id_str(assessment_id, db)
        return self.to_payload(row) if row is not None else None

    async def create_attempt(
        self,
        *,
        assessment_id: str | UUID,
        learner_id: str | UUID,
        responses: list[dict[str, Any]],
        score: float,
        marks_obtained: int,
        time_taken_seconds: int,
        db: AsyncSession | None = None,
    ) -> str:
        """Create an attempt and return its ID as the V2 service expects."""
        attempt = await AssessmentAttemptRepository().create_attempt(
            self._resolve_db(db),
            assessment_id=assessment_id,
            learner_id=learner_id,
            responses={"responses": responses},
            score=score,
            marks_obtained=marks_obtained,
            time_taken_seconds=time_taken_seconds,
        )
        return str(attempt.id)

    @staticmethod
    def to_payload(row: Assessment) -> dict[str, Any]:
        questions = row.questions or []
        if isinstance(questions, dict):
            questions = questions.get("questions", questions.get("items", []))
        return {
            "assessment_id": str(row.id),
            "id": str(row.id),
            "title": row.title,
            "subject_code": row.subject_code,
            "grade_level": row.grade_level,
            "assessment_type": row.assessment_type,
            "total_marks": row.total_marks,
            "questions": questions,
            "passing_score": row.passing_score,
            "is_active": row.is_active,
        }


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
            assessment_id=str(assessment_id),
            learner_id=str(learner_id),
            score=score,
            marks_obtained=marks_obtained,
            time_taken_seconds=time_taken_seconds,
            responses=responses,
        )
