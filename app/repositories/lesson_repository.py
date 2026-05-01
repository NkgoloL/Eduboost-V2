"""Lesson persistence repository for EduBoost V2."""

from __future__ import annotations

from sqlalchemy import insert, select

from app.api.core.database import AsyncSessionFactory
from app.api.models.db_models import Lesson as LessonRecord


class LessonRepository:
    async def create(self, lesson: dict, grade_level: int) -> None:
        async with AsyncSessionFactory() as session:
            await session.execute(
                insert(LessonRecord).values(
                    lesson_id=lesson["lesson_id"],
                    title=lesson["title"],
                    subject_code=lesson["subject_code"],
                    grade_level=grade_level,
                    topic=lesson["topic"],
                    content=lesson["content"],
                    content_modality="text",
                    duration_minutes=15,
                    difficulty_level=0.5,
                    learning_objectives=[lesson["topic"]],
                    prerequisites=[],
                    is_cap_aligned=True,
                    is_active=True,
                )
            )
            await session.commit()

    async def get_by_id(self, lesson_id: str) -> LessonRecord | None:
        async with AsyncSessionFactory() as session:
            result = await session.execute(select(LessonRecord).where(LessonRecord.lesson_id == lesson_id))
            return result.scalar_one_or_none()
