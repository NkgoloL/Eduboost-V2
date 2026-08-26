"""Service layer for human review and coverage metrics of generated lessons."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.lesson import ReviewStatus, SafetyClassification
from app.repositories.lesson_repository import LessonRepository


class LessonReviewService:
    def __init__(self, repository: LessonRepository) -> None:
        self.repository = repository

    @classmethod
    def from_session(cls, session: Any) -> LessonReviewService:
        return cls(repository=LessonRepository(session))

    async def list_pending_review(
        self,
        *,
        grade: int | None = None,
        subject: str | None = None,
        caps_ref: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Any]:
        return await self.repository.list_pending_review(
            grade=grade, subject=subject, caps_ref=caps_ref, limit=limit, offset=offset
        )

    async def list_by_caps_ref(self, caps_ref: str, include_all_statuses: bool = True) -> list[Any]:
        return await self.repository.list_by_caps_ref(caps_ref, include_all_statuses=include_all_statuses)

    async def review_lesson(
        self,
        lesson_id: UUID,
        decision: str,
        reviewer_id: UUID,
        reviewer_notes: str | None = None,
    ) -> Any | None:
        return await self.repository.update_review_status(
            lesson_id, review_status=decision, reviewer_id=reviewer_id, reviewer_notes=reviewer_notes
        )


def get_lesson_review_service(db: AsyncSession = Depends(get_db)) -> LessonReviewService:
    return LessonReviewService.from_session(db)
