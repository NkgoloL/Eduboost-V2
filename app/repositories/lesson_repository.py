"""Lesson persistence repository for EduBoost V2."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Lesson


class LessonRepository:
    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db

    def _db(self, db: AsyncSession | None = None) -> AsyncSession:
        session = db or self.db
        if session is None:
            raise RuntimeError("LessonRepository requires an AsyncSession")
        return session

    async def create(self, *args: Any, **kwargs: Any) -> Lesson:
        explicit_db = kwargs.pop("db", None)
        db = args[0] if args and isinstance(args[0], AsyncSession) else self._db(explicit_db)
        lesson = Lesson(**kwargs)
        db.add(lesson)
        await db.flush()
        await db.refresh(lesson)
        return lesson

    async def get(self, lesson_id: str | UUID, db: AsyncSession | None = None) -> Lesson | None:
        result = await self._db(db).execute(select(Lesson).where(Lesson.id == str(lesson_id)))
        return result.scalar_one_or_none()

    async def get_recent_for_learner(
        self,
        learner_id: UUID | str,
        db: AsyncSession | None = None,
        *,
        subject: str | None = None,
        limit: int = 10,
    ) -> list[Lesson]:
        stmt = (
            select(Lesson)
            .where(Lesson.learner_id == str(learner_id))
            .order_by(Lesson.created_at.desc())
            .limit(limit)
        )
        if subject:
            stmt = stmt.where(Lesson.subject == subject)
        result = await self._db(db).execute(stmt)
        return list(result.scalars().all())

    async def get_recent(self, learner_id: UUID | str, skip: int = 0, limit: int = 10) -> list[Lesson]:
        stmt = (
            select(Lesson)
            .where(Lesson.learner_id == str(learner_id))
            .order_by(Lesson.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._db().execute(stmt)
        return list(result.scalars().all())

    async def list_pending_review(
        self,
        *,
        grade: int | None = None,
        subject: str | None = None,
        caps_ref: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Lesson]:
        stmt = select(Lesson).where(Lesson.review_status == "ai_generated")
        stmt = stmt.where(
            (Lesson.quality_score < 0.7)
            | (Lesson.answer_key_verified.is_(False))
            | (Lesson.safety_classification == "requires_review")
        )
        if grade is not None:
            stmt = stmt.where(Lesson.grade == grade)
        if subject:
            stmt = stmt.where(Lesson.subject == subject)
        if caps_ref:
            stmt = stmt.where(Lesson.caps_ref == caps_ref)
        stmt = stmt.order_by(Lesson.quality_score.asc(), Lesson.created_at.asc()).offset(offset).limit(limit)
        result = await self._db().execute(stmt)
        return list(result.scalars().all())

    async def list_by_caps_ref(self, caps_ref: str, include_all_statuses: bool = False) -> list[Lesson]:
        stmt = select(Lesson).where(Lesson.caps_ref == caps_ref)
        if not include_all_statuses:
            stmt = stmt.where(Lesson.review_status == "approved")
        result = await self._db().execute(stmt)
        return list(result.scalars().all())

    async def update_review_status(
        self,
        lesson_id: str | UUID,
        *,
        review_status: str,
        reviewer_id: str | UUID,
        reviewer_notes: str | None = None,
    ) -> Lesson | None:
        lesson = await self.get(lesson_id)
        if lesson is None:
            return None
        lesson.review_status = review_status
        lesson.reviewer_id = UUID(str(reviewer_id))
        lesson.reviewed_at = datetime.now(UTC)
        trust_label = dict(lesson.trust_label or {})
        if reviewer_notes:
            trust_label["reviewer_notes"] = reviewer_notes
        lesson.trust_label = trust_label
        self._db().add(lesson)
        await self._db().flush()
        await self._db().refresh(lesson)
        return lesson

    async def record_feedback(self, lesson_id: str, score: int) -> None:
        await self._db().execute(update(Lesson).where(Lesson.id == lesson_id).values(feedback_score=score))

    async def mark_completed(self, lesson_id: str, completed_at: datetime | None = None) -> None:
        await self._db().execute(
            update(Lesson).where(Lesson.id == lesson_id).values(completed_at=completed_at or datetime.now(UTC))
        )

    async def count_approved_by_caps_ref_async(self, caps_ref: str) -> int:
        result = await self._db().execute(
            select(func.count()).select_from(Lesson).where(Lesson.caps_ref == caps_ref, Lesson.review_status == "approved")
        )
        return int(result.scalar_one())

    async def list_approved_lessons_async(self) -> list[dict[str, Any]]:
        result = await self._db().execute(
            select(Lesson).where(Lesson.review_status == "approved").order_by(Lesson.caps_ref.asc(), Lesson.created_at.asc())
        )
        return [self._to_validator_payload(lesson) for lesson in result.scalars().all()]

    @staticmethod
    def _to_validator_payload(lesson: Lesson) -> dict[str, Any]:
        return {
            "lesson_id": lesson.id,
            "grade": lesson.grade,
            "subject": lesson.subject,
            "topic": lesson.topic,
            "caps_ref": lesson.caps_ref,
            "explanation": lesson.explanation or lesson.content,
            "worked_examples": lesson.worked_examples or [],
            "practice_questions": lesson.practice_questions or [],
            "answer_key": lesson.answer_key or [],
            "answer_key_verified": lesson.answer_key_verified,
            "provider": lesson.provider or lesson.llm_provider or "unknown",
            "model_version": lesson.model_version or "unknown",
            "generation_latency_ms": lesson.generation_latency_ms,
            "token_usage": lesson.token_usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "prompt_template_version": lesson.prompt_template_version or "lesson_generation_v1",
            "variant_type": lesson.variant_type or "standard",
        }


def get_lesson_repository(db: AsyncSession = Depends(get_db)) -> LessonRepository:
    return LessonRepository(db)
