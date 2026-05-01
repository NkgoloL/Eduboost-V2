"""V2 lesson generation and retrieval service."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import uuid

import redis.asyncio as redis_async

from app.core.config import get_v2_settings
from app.repositories.lesson_repository import LessonRepository
from app.services.audit_service import AuditService
from app.services.quota_service import QuotaService


class LessonServiceV2:
    def __init__(self, lesson_repository: LessonRepository | None = None) -> None:
        settings = get_v2_settings()
        self.redis = redis_async.from_url(settings.redis_url, decode_responses=True)
        self.quota_service = QuotaService()
        self.lesson_repository = lesson_repository or LessonRepository()

    async def generate_lesson(self, learner_id: str, subject_code: str, topic: str, grade_level: int = 4) -> dict:
        await self.quota_service.assert_within_quota(f"lesson:{learner_id}")
        cache_payload = {"learner_id": learner_id, "subject_code": subject_code, "topic": topic, "grade_level": grade_level}
        cached = await self.quota_service.get_cached("lesson", cache_payload)
        if cached is not None:
            return cached

        lesson_id = str(uuid.uuid4())
        lesson = {
            "lesson_id": lesson_id,
            "learner_id": learner_id,
            "subject_code": subject_code,
            "topic": topic,
            "title": f"{subject_code} — {topic}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "content": json.dumps({
                "story_hook": f"Let's learn about {topic}.",
                "steps": ["Warm up", "Concept", "Practice", "Reflect"],
            }),
            "generated_by": "V2_ALGORITHM",
        }

        await self.lesson_repository.create(lesson=lesson, grade_level=grade_level)
        await self.redis.set(f"v2:lesson:{lesson_id}", json.dumps(lesson), ex=3600)
        await self.quota_service.set_cached("lesson", cache_payload, lesson)
        await AuditService().log_event(
            event_type="LESSON_GENERATED",
            learner_id=learner_id,
            payload={"lesson_id": lesson_id, "subject_code": subject_code, "topic": topic},
        )
        return lesson

    async def get_lesson(self, lesson_id: str) -> dict | None:
        raw = await self.redis.get(f"v2:lesson:{lesson_id}")
        if raw is not None:
            return json.loads(raw)

        row = await self.lesson_repository.get_by_id(lesson_id)
        if row is None:
            return None
        return {
            "lesson_id": row.lesson_id,
            "title": row.title,
            "subject_code": row.subject_code,
            "grade_level": row.grade_level,
            "topic": row.topic,
            "content": row.content,
            "source": "database",
        }
