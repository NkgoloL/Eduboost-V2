"""Lesson routes for EduBoost V2."""

from fastapi import APIRouter, HTTPException, Depends

from app.domain.api_v2_models import LessonGenerateRequest
from app.services.lesson_service_v2 import LessonServiceV2
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v2/lessons", tags=["V2 Lessons"])


@router.post("/generate")
async def generate_lesson(request: LessonGenerateRequest, user: dict = Depends(get_current_user)):
    # Basic role check
    if user.get("role") not in {"Student", "Parent", "Admin"}:
        raise HTTPException(status_code=403, detail="Forbidden")

    from app.services.analytics_service import AnalyticsService
    await AnalyticsService().track_event("lesson_requested", request.learner_id, {"topic": request.topic})
    
    return await LessonServiceV2().generate_lesson(
        learner_id=request.learner_id,
        subject_code=request.subject_code,
        topic=request.topic,
        grade_level=request.grade_level,
    )


@router.get("/{lesson_id}")
async def get_lesson(lesson_id: str):
    lesson = await LessonServiceV2().get_lesson(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson
