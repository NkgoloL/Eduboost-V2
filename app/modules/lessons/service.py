from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models import KnowledgeGap, Lesson
from app.repositories.repositories import (
    GuardianRepository,
    LearnerRepository,
    LessonRepository,
)
from app.services.consent import ConsentService
from app.services.executive import ExecutiveService, QuotaExceededError
from app.services.fourth_estate import FourthEstateService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.domain.schemas import LessonRequest, LessonResponse


class LessonService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._executive = ExecutiveService()
        self._lesson_repo = LessonRepository(db)
        self._learner_repo = LearnerRepository(db)
        self._guardian_repo = GuardianRepository(db)
        self._consent_service = ConsentService(db)
        self._audit_service = FourthEstateService(db)

    async def generate_lesson_for_learner(
        self, body: LessonRequest, current_user_id: UUID
    ) -> tuple[LessonResponse, bool, str]:
        # 1. Consent Gate
        await self._consent_service.require_active_consent(
            body.learner_id, actor_id=str(current_user_id)
        )

        # 2. Build Context
        learner = await self._learner_repo.get_by_id(body.learner_id)
        if not learner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found"
            )

        guardian = await self._guardian_repo.get_by_id(learner.guardian_id)
        tier = guardian.subscription_tier if guardian else "free"
        
        learner_context = await self._build_learner_context(body.learner_id, body.subject)

        # 3. Call AI Service (Executive/Ether)
        try:
            payload, from_cache = await self._executive.generate_lesson(
                pseudonym_id=learner.pseudonym_id,
                grade=learner.grade,
                subject=body.subject,
                topic=body.topic,
                language=body.language,
                archetype=learner.archetype,
                user_id=learner.guardian_id,
                tier=tier,
                learner_context=learner_context,
            )
        except QuotaExceededError as exc:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily AI quota exceeded. Upgrade to Premium for unlimited access.",
            ) from exc

        # 4. Persist and Audit
        provider = "cache" if from_cache else "groq"
        lesson = await self._lesson_repo.create(
            learner_id=body.learner_id,
            grade=learner.grade,
            subject=body.subject,
            topic=body.topic,
            language=body.language,
            archetype=learner.archetype,
            content=self._render_lesson_content(payload),
            llm_provider=provider,
            served_from_cache=from_cache,
        )
        
        await self._audit_service.lesson_generated(
            learner.pseudonym_id, body.subject, body.topic, provider
        )
        
        # Note: Caller is responsible for commit if needed, or we can commit here
        await self.db.commit()

        from app.domain.schemas import LessonResponse
        return (
            LessonResponse.model_validate(lesson).model_copy(
                update={"cache_hit": from_cache, "caps_aligned": True}
            ),
            from_cache,
            provider,
        )

    async def _build_learner_context(self, learner_id: str, subject: str) -> dict:
        gaps_result = await self.db.execute(
            select(KnowledgeGap.topic, KnowledgeGap.severity)
            .where(
                KnowledgeGap.learner_id == learner_id,
                KnowledgeGap.resolved == False,  # noqa: E712
                KnowledgeGap.subject == subject,
            )
            .order_by(KnowledgeGap.severity.desc())
            .limit(3)
        )
        recent_lessons = await self._lesson_repo.get_recent(learner_id, limit=3)
        return {
            "knowledge_gaps": [
                {"topic": topic, "severity": severity}
                for topic, severity in gaps_result.all()
            ],
            "recent_lessons": [
                {
                    "subject": lesson.subject,
                    "topic": lesson.topic,
                    "completed": lesson.completed_at is not None,
                }
                for lesson in recent_lessons
            ],
        }

    def _render_lesson_content(self, payload) -> str:
        return (
            f"# {payload.title}\n\n{payload.introduction}\n\n{payload.main_content}\n\n"
            f"## Worked Example\n{payload.worked_example}\n\n"
            f"## Practice\n{payload.practice_question}\n\n**Answer:** {payload.answer}\n\n"
            f"---\n*{payload.cultural_hook}*"
        )
