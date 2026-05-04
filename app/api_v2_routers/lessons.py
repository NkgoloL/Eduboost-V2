"""EduBoost V2 — Lessons Router"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db
from app.core.jobs import enqueue_job
from app.core.rate_limit import limiter, LESSON_GENERATION_LIMIT, LESSON_GENERATION_PREMIUM_LIMIT
from app.core.security import get_current_user
from app.domain.api_v2_models import JobAcceptedResponse
from app.domain.schemas import LessonFeedback, LessonRequest, LessonResponse
from app.models import Lesson
from app.repositories.repositories import GuardianRepository, LearnerRepository, LessonRepository
from app.services.consent import ConsentService
from app.services.executive import ExecutiveService, QuotaExceededError
from app.services.fourth_estate import FourthEstateService

router = APIRouter(prefix="/lessons", tags=["lessons"])
_executive = ExecutiveService()


def _render_lesson_content(payload) -> str:
    return (
        f"# {payload.title}\n\n{payload.introduction}\n\n{payload.main_content}\n\n"
        f"## Worked Example\n{payload.worked_example}\n\n"
        f"## Practice\n{payload.practice_question}\n\n**Answer:** {payload.answer}\n\n"
        f"---\n*{payload.cultural_hook}*"
    )


@router.post("/generate", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
@router.post("/", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("10/day")  # Default rate limit; will be enhanced with per-tier logic below
async def generate_lesson(
    request: Request,
    body: LessonRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    async def _run() -> dict:
        async with AsyncSessionLocal() as db:
            await ConsentService(db).require_active_consent(body.learner_id, actor_id=current_user.get("sub"))
            learner_repo = LearnerRepository(db)
            learner = await learner_repo.get_by_id(body.learner_id)
            if not learner:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

            guardian = await GuardianRepository(db).get_by_id(learner.guardian_id)
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
            except QuotaExceededError as exc:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Daily AI quota exceeded. Upgrade to Premium for unlimited access.",
                ) from exc

            lesson = await LessonRepository(db).create(
                learner_id=body.learner_id,
                grade=learner.grade,
                subject=body.subject,
                topic=body.topic,
                language=body.language,
                archetype=learner.archetype,
                content=_render_lesson_content(payload),
                llm_provider="groq",
                served_from_cache=from_cache,
            )
            await FourthEstateService(db).lesson_generated(learner.pseudonym_id, body.subject, body.topic, "groq")
            await db.commit()
            return LessonResponse.model_validate(lesson).model_dump(mode="json")

    job = await enqueue_job(
        background_tasks,
        operation="lesson_generation",
        payload={"learner_id": body.learner_id, "subject": body.subject, "topic": body.topic},
        handler=_run,
    )
    return JobAcceptedResponse(job_id=job["job_id"], operation=job["operation"], status=job["status"])


@router.get("/{lesson_id}")
async def get_lesson(
    lesson_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    await ConsentService(db).require_active_consent(lesson.learner_id, actor_id=current_user.get("sub"))
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
