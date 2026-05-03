"""EduBoost V2 — Lessons Router"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.schemas import LessonFeedback, LessonRequest, LessonResponse
from app.repositories.repositories import GuardianRepository, LearnerRepository, LessonRepository
from app.services.consent import ConsentService
from app.services.executive import ExecutiveService, QuotaExceededError
from app.services.fourth_estate import FourthEstateService

router = APIRouter(prefix="/lessons", tags=["lessons"])
_executive = ExecutiveService()


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def generate_lesson(
    body: LessonRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Consent gate
    await ConsentService(db).require_active_consent(body.learner_id)

    learner_repo = LearnerRepository(db)
    learner = await learner_repo.get_by_id(body.learner_id)
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

    # Fetch guardian tier for quota
    guardian_repo = GuardianRepository(db)
    guardian = await guardian_repo.get_by_id(learner.guardian_id)
    tier = guardian.subscription_tier if guardian else "free"

    try:
        payload, from_cache = await _executive.generate_lesson(
            pseudonym_id=learner.pseudonym_id,
            grade=learner.grade,
            subject=body.subject,
            topic=body.topic,
            language=body.language,
            archetype=learner.archetype,
            user_id=learner.guardian_id,
            tier=tier,
        )
    except QuotaExceededError:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Daily AI quota exceeded. Upgrade to Premium for unlimited access.")

    # Persist lesson
    lesson_repo = LessonRepository(db)
    content_text = (
        f"# {payload.title}\n\n{payload.introduction}\n\n{payload.main_content}\n\n"
        f"## Worked Example\n{payload.worked_example}\n\n"
        f"## Practice\n{payload.practice_question}\n\n**Answer:** {payload.answer}\n\n"
        f"---\n*{payload.cultural_hook}*"
    )
    lesson = await lesson_repo.create(
        learner_id=body.learner_id,
        grade=learner.grade,
        subject=body.subject,
        topic=body.topic,
        language=body.language,
        archetype=learner.archetype,
        content=content_text,
        llm_provider="groq",
        served_from_cache=from_cache,
    )

    audit = FourthEstateService(db)
    await audit.lesson_generated(learner.pseudonym_id, body.subject, body.topic, "groq")

    return LessonResponse.model_validate(lesson)


@router.post("/{lesson_id}/feedback")
async def submit_feedback(
    lesson_id: str,
    body: LessonFeedback,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    await LessonRepository(db).record_feedback(lesson_id, body.score)
    return {"detail": "Feedback recorded. Thank you!"}
