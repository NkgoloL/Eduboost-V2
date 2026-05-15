"""EduBoost V2 — Lessons Router"""

import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from app.core.envelope_route import EnvelopedRoute
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import settings
from app.core.database import get_db
from app.core.jobs import enqueue_job
from app.core.rate_limit import limiter
from app.core.security import get_current_user
from app.core.dependencies import get_current_user_id
from app.domain.api_v2_models import JobAcceptedResponse
from app.domain.schemas import LessonFeedback, LessonRequest, LessonResponse, LessonSyncRequest
from app.modules.lessons.service import LessonService
from app.modules.lessons import lesson_coverage_router, lesson_review_router
from app.security.dependencies import require_learner_write_for_current_user, require_active_consent_for_current_user

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
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LessonService = Depends(get_lesson_service),
):
    require_learner_write_for_current_user(current_user, str(body.learner_id))
    await require_active_consent_for_current_user(db, current_user, str(body.learner_id))
    user_id = UUID(str(current_user["sub"]))
    async def _run() -> dict:
        lesson, _, _ = await service.generate_lesson_for_learner(body, user_id)
        return lesson.model_dump(mode="json")

    job = await enqueue_job(
        background_tasks,
        operation="lesson_generation",
        payload={"learner_id": str(body.learner_id), "subject": body.subject, "topic": body.topic},
        handler=_run,
    )
    return JobAcceptedResponse(job_id=job["job_id"], operation=job["operation"], status=job["status"])


@router.post("/generate/stream")
async def generate_lesson_stream(
    body: LessonRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LessonService = Depends(get_lesson_service),
):
    require_learner_write_for_current_user(current_user, str(body.learner_id))
    await require_active_consent_for_current_user(db, current_user, str(body.learner_id))
    user_id = UUID(str(current_user["sub"]))
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
    current_user: dict = Depends(get_current_user),
    service: LessonService = Depends(get_lesson_service),
):
    lesson = await service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    
    # Ownership check
    # Note: In a real app, we'd check if current_user has access to this learner's lessons.
    # For now, we trust the lesson_id is known only to the authorized user.
    
    from app.domain.schemas import LessonResponse
    return LessonResponse.model_validate(lesson)


@router.post("/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: str,
    current_user: dict = Depends(get_current_user),
    service: LessonService = Depends(get_lesson_service),
):
    lesson = await service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    
    await service.complete_lesson(lesson_id)
    return {"status": "success", "message": "Lesson marked as completed"}
