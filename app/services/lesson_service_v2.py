from __future__ import annotations

import json
import uuid
from typing import Any

from app.services.audit_service import AuditService
from app.services.quota_service import QuotaService, SemanticCacheService


async def _call_llm(*_: Any, **__: Any) -> dict:
    return {
        "story_hook": "A South African classroom example.",
        "learning_objectives": [],
        "key_concepts": [],
        "worked_example": "",
        "practice_questions": [],
        "reflection": "",
    }


class LessonServiceV2:
    def __init__(self, lesson_repository: Any, redis_client: Any | None = None) -> None:
        self.lesson_repository = lesson_repository
        self.redis = redis_client
        self.quota_service = QuotaService(redis_client) if redis_client else None
        self.cache_service = SemanticCacheService(redis_client) if redis_client else None

    async def generate_lesson(
        self,
        learner_id: str,
        subject_code: str,
        topic: str,
        grade_level: int | None = None,
        language: str = "en",
        archetype: str | None = None,
        tier: str = "free",
    ) -> dict:
        key = None
        if self.cache_service:
            key = self.cache_service.build_cache_key(subject_code, topic, str(grade_level or ""), language, archetype)
            cached = await self.cache_service.get(key)
            if cached:
                return json.loads(cached) if isinstance(cached, str) else cached

        if self.quota_service:
            await self.quota_service.check_and_reserve(learner_id, estimated_tokens=1000, tier=tier)

        content = await _call_llm(learner_id=learner_id, subject_code=subject_code, topic=topic, grade_level=grade_level)
        lesson_id = str(uuid.uuid4())
        row = await self.lesson_repository.create(
            db=None,  # Or whatever is needed for V2
            id=lesson_id,
            learner_id=learner_id,
            subject=subject_code,
            grade=grade_level or 0,
            topic=topic,
            content=json.dumps(content),
            generated_by="V2_LLM",
        )
        result = {
            "lesson_id": getattr(row, "id", lesson_id),
            "learner_id": learner_id,
            "subject_code": subject_code,
            "topic": topic,
            "content": content,
            "generated_by": "V2_LLM",
        }
        if self.cache_service and key:
            await self.cache_service.set(key, json.dumps(result))

        await AuditService().log_event("LESSON_GENERATED", {"subject_code": subject_code, "topic": topic}, learner_id)
        return result

    async def get_lesson(self, lesson_id: str) -> dict | None:
        if self.redis is not None:
            cached = await self.redis.get(f"lesson:{lesson_id}")
            if cached:
                return json.loads(cached) if isinstance(cached, str) else cached
        row = await self.lesson_repository.get_by_id(lesson_id)
        if row is None:
            return None
        return {
            "lesson_id": getattr(row, "lesson_id", lesson_id),
            "title": getattr(row, "title", ""),
            "subject_code": getattr(row, "subject_code", ""),
            "grade_level": getattr(row, "grade_level", None),
            "topic": getattr(row, "topic", ""),
            "content": getattr(row, "content", {}),
            "generated_by": getattr(row, "generated_by", "V2_LLM"),
            "source": "database",
        }

    async def submit_feedback(self, lesson_id: str, learner_id: str, rating: int, comment: str | None = None) -> dict:
        await AuditService().log_event("LESSON_FEEDBACK", {"lesson_id": lesson_id, "rating": rating, "comment": comment}, learner_id)
        return {"recorded": True, "lesson_id": lesson_id}
