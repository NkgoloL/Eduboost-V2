"""Lesson routes for EduBoost V2."""

from fastapi import APIRouter, HTTPException

from app.domain.api_v2_models import LessonGenerateRequest
from app.services.lesson_service_v2 import LessonServiceV2

router = APIRouter(prefix="/api/v2/lessons", tags=["V2 Lessons"])


@router.post("/generate")
async def generate_lesson(request: LessonGenerateRequest):
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
