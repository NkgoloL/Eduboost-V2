"""EduBoost V2 — Lessons Router"""

import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.envelope_route import EnvelopedRoute
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.domain.api_v2_models import JobAcceptedResponse
from app.domain.schemas import LessonRequest, LessonResponse, LessonSyncRequest
from app.modules.lessons.service import LessonService
from app.modules.lessons import lesson_coverage_router, lesson_review_router
from app.modules.jobs import enqueue_durable
from app.services.lesson_authorization import (
    iter_sync_lesson_ids,
    require_lesson_read_access_for_current_user,
    require_lesson_write_access_for_current_user,
)
from app.security.dependencies import (
    require_active_consent_for_current_user,
    require_learner_write_for_current_user,
)

router = APIRouter(route_class=EnvelopedRoute, prefix="/lessons", tags=["lessons"])
router.include_router(lesson_review_router.router)
router.include_router(lesson_coverage_router.router)

async def get_lesson_service(db: AsyncSession = Depends(get_db)) -> LessonService:
    return LessonService(db)


@router.post("/generate", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
@router.post("/", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit(settings.RATE_LIMIT_LLM)
async def generate_lesson(
    request: Request,
    body: LessonRequest,
    auth: AuthContext = Depends(require_auth_context),
    db: AsyncSession = Depends(get_db),
):
    require_learner_write_for_current_user(auth, str(body.learner_id))
    await require_active_consent_for_current_user(db, auth, str(body.learner_id))

    job_id = await enqueue_durable(
        "generate_lesson_job",
        operation="lesson_generation",
        payload={
            "learner_id": str(body.learner_id),
            "subject": body.subject,
            "topic": body.topic,
            "language": body.language,
            "current_user_id": str(auth.user_id),
        },
        kwargs={
            "learner_id": str(body.learner_id),
            "subject": body.subject,
            "topic": body.topic,
            "language": body.language,
            "current_user_id": str(auth.user_id),
        },
    )
    return JobAcceptedResponse(job_id=job_id, operation="lesson_generation", status="queued")


@router.post("/generate/stream")
async def generate_lesson_stream(
    body: LessonRequest,
    auth: AuthContext = Depends(require_auth_context),
    db: AsyncSession = Depends(get_db),
    service: LessonService = Depends(get_lesson_service),
):
    require_learner_write_for_current_user(auth, str(body.learner_id))
    await require_active_consent_for_current_user(db, auth, str(body.learner_id))
    user_id = UUID(str(auth.user_id))

    async def _events():
        yield f"event: status\ndata: {json.dumps({'status': 'accepted', 'operation': 'lesson_generation'})}\n\n"
        try:
            lesson, from_cache, provider = await service.generate_lesson_for_learner(body, user_id)
            yield f"event: result\ndata: {lesson.model_dump_json()}\n\n"
            yield f"event: done\ndata: {json.dumps({'status': 'completed', 'cache_hit': from_cache, 'provider': provider})}\n\n"
        except HTTPException as exc:
            yield f"event: error\ndata: {json.dumps({'status': 'failed', 'message': exc.detail})}\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"event: error\ndata: {json.dumps({'status': 'failed', 'message': str(exc)})}\n\n"

    return StreamingResponse(_events(), media_type="text/event-stream")

@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: str,
    auth: AuthContext = Depends(require_auth_context),
    service: LessonService = Depends(get_lesson_service),
    db: AsyncSession = Depends(get_db),
):
    # code_611_630_lesson_read_authz
    await require_lesson_read_access_for_current_user(db, auth, lesson_id)
    lesson = await service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    return LessonResponse.model_validate(lesson)


@router.post("/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: str,
    auth: AuthContext = Depends(require_auth_context),
    service: LessonService = Depends(get_lesson_service),
    db: AsyncSession = Depends(get_db),
):
    # code_611_630_lesson_write_authz
    await require_lesson_write_access_for_current_user(db, auth, lesson_id)
    lesson = await service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    await service.complete_lesson(lesson_id)
    return {"status": "success", "message": "Lesson marked as completed"}


@router.post("/sync")
async def sync_lessons(
    body: LessonSyncRequest,
    auth: AuthContext = Depends(require_auth_context),
    service: LessonService = Depends(get_lesson_service),
    db: AsyncSession = Depends(get_db),
):
    # code_611_630_lesson_sync_authz
    for _lesson_id in iter_sync_lesson_ids(body):
        await require_lesson_write_access_for_current_user(db, auth, _lesson_id)

    processed = 0
    for event in body.responses:
        if event.event_type == "complete":
            await service.complete_lesson(event.lesson_id)
            processed += 1
        elif event.event_type == "feedback" and event.score is not None:
            await service.record_feedback(event.lesson_id, event.score)
            processed += 1

    return {"status": "success", "processed": processed}
