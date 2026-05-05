"""EduBoost V2 — Lessons Router"""

from datetime import UTC, datetime
import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db
from app.core.jobs import enqueue_job
from app.core.rate_limit import limiter, LESSON_GENERATION_LIMIT, LESSON_GENERATION_PREMIUM_LIMIT
from app.core.security import get_current_user
from app.domain.api_v2_models import JobAcceptedResponse
from app.domain.schemas import LessonFeedback, LessonRequest, LessonResponse, LessonSyncRequest
from app.models import KnowledgeGap, Lesson
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


async def _build_learner_context(db: AsyncSession, learner_id: str, subject: str) -> dict:
    gaps_result = await db.execute(
        select(KnowledgeGap.topic, KnowledgeGap.severity)
        .where(
            KnowledgeGap.learner_id == learner_id,
            KnowledgeGap.resolved == False,  # noqa: E712
            KnowledgeGap.subject == subject,
        )
        .order_by(KnowledgeGap.severity.desc())
        .limit(3)
    )
    recent_lessons = await LessonRepository(db).get_recent(learner_id, limit=3)
    return {
        "knowledge_gaps": [
            {"topic": topic, "severity": severity}
            for topic, severity in gaps_result.all()
        ],
        "recent_lessons": [
            {"subject": lesson.subject, "topic": lesson.topic, "completed": lesson.completed_at is not None}
            for lesson in recent_lessons
        ],
    }


async def _create_lesson_for_request(body: LessonRequest, current_user: dict) -> tuple[LessonResponse, bool, str]:
    async with AsyncSessionLocal() as db:
        await ConsentService(db).require_active_consent(body.learner_id, actor_id=current_user.get("sub"))
        learner_repo = LearnerRepository(db)
        learner = await learner_repo.get_by_id(body.learner_id)
        if not learner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

        guardian = await GuardianRepository(db).get_by_id(learner.guardian_id)
        tier = guardian.subscription_tier if guardian else "free"
        learner_context = await _build_learner_context(db, body.learner_id, body.subject)
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
                learner_context=learner_context,
            )
        except QuotaExceededError as exc:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily AI quota exceeded. Upgrade to Premium for unlimited access.",
            ) from exc

        provider = "cache" if from_cache else "groq"
        lesson = await LessonRepository(db).create(
            learner_id=body.learner_id,
            grade=learner.grade,
            subject=body.subject,
            topic=body.topic,
            language=body.language,
            archetype=learner.archetype,
            content=_render_lesson_content(payload),
            llm_provider=provider,
            served_from_cache=from_cache,
        )
        await FourthEstateService(db).lesson_generated(learner.pseudonym_id, body.subject, body.topic, provider)
        await db.commit()
        return (
            LessonResponse.model_validate(lesson).model_copy(
                update={"cache_hit": from_cache, "caps_aligned": True}
            ),
            from_cache,
            provider,
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
        lesson, _, _ = await _create_lesson_for_request(body, current_user)
        return lesson.model_dump(mode="json")

    job = await enqueue_job(
        background_tasks,
        operation="lesson_generation",
        payload={"learner_id": body.learner_id, "subject": body.subject, "topic": body.topic},
        handler=_run,
    )
    return JobAcceptedResponse(job_id=job["job_id"], operation=job["operation"], status=job["status"])


@router.post("/generate/stream")
async def generate_lesson_stream(
    body: LessonRequest,
    current_user: dict = Depends(get_current_user),
):
    async def _events():
        yield f"event: status\ndata: {json.dumps({'status': 'accepted', 'operation': 'lesson_generation'})}\n\n"
        try:
            lesson, from_cache, provider = await _create_lesson_for_request(body, current_user)
            yield f"event: result\ndata: {lesson.model_dump_json()}\n\n"
            yield f"event: done\ndata: {json.dumps({'status': 'completed', 'cache_hit': from_cache, 'provider': provider})}\n\n"
        except HTTPException as exc:
            yield f"event: error\ndata: {json.dumps({'status': 'failed', 'message': exc.detail})}\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"event: error\ndata: {json.dumps({'status': 'failed', 'message': str(exc)})}\n\n"

    return StreamingResponse(_events(), media_type="text/event-stream")


@router.get("/{lesson_id}")
async def get_lesson(
    lesson_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    await ConsentService(db).require_active_consent(lesson.learner_id, actor_id=current_user.get("sub"))
    learner = await LearnerRepository(db).get_by_id(lesson.learner_id)
    if learner is not None:
        request.state.analytics = {
            "event": "lesson_viewed",
            "pseudonym_id": learner.pseudonym_id,
            "properties": {"subject": lesson.subject, "topic": lesson.topic},
        }
    return LessonResponse.model_validate(lesson).model_copy(
        update={"cache_hit": lesson.served_from_cache, "caps_aligned": True}
    )


@router.post("/{lesson_id}/feedback")
async def submit_feedback(
    lesson_id: str,
    body: LessonFeedback,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    lesson = await db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    await ConsentService(db).require_active_consent(lesson.learner_id, actor_id=current_user.get("sub"))
    await LessonRepository(db).record_feedback(lesson_id, body.score)
    await db.commit()
    learner = await LearnerRepository(db).get_by_id(lesson.learner_id) if lesson else None
    if learner is not None:
        request.state.analytics = {
            "event": "lesson_feedback_submitted",
            "pseudonym_id": learner.pseudonym_id,
            "properties": {"score": body.score},
        }
    return {"detail": "Feedback recorded. Thank you!"}


@router.post("/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    await ConsentService(db).require_active_consent(lesson.learner_id, actor_id=current_user.get("sub"))
    await LessonRepository(db).mark_completed(lesson_id)
    learner = await LearnerRepository(db).get_by_id(lesson.learner_id)
    if learner is not None:
        request.state.analytics = {
            "event": "lesson_completed",
            "pseudonym_id": learner.pseudonym_id,
            "properties": {"lesson_id": lesson_id, "subject": lesson.subject},
        }
    await db.commit()
    return {"detail": "Lesson marked complete."}


@router.post("/sync")
async def sync_lesson_responses(
    body: LessonSyncRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    processed = 0
    for event in body.responses:
        lesson = await db.get(Lesson, event.lesson_id)
        if lesson is None:
            continue
        await ConsentService(db).require_active_consent(lesson.learner_id, actor_id=current_user.get("sub"))
        repo = LessonRepository(db)
        if event.event_type == "complete":
            await repo.mark_completed(
                event.lesson_id,
                completed_at=event.completed_at or datetime.now(UTC),
            )
        elif event.event_type == "feedback" and event.score is not None:
            await repo.record_feedback(event.lesson_id, event.score)
        processed += 1
        learner = await LearnerRepository(db).get_by_id(lesson.learner_id)
        if learner is not None:
            request.state.analytics = {
                "event": "lesson_completed" if event.event_type == "complete" else "lesson_feedback_submitted",
                "pseudonym_id": learner.pseudonym_id,
                "properties": {"lesson_id": lesson.id, "score": event.score},
            }

    await db.commit()
    return {"processed": processed, "queued": max(0, len(body.responses) - processed)}
