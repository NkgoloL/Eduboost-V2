from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.modules.lessons.lesson_schema_v1 import (
    DifficultyLevel,
    LLMProvider,
    LessonCreate,
    LessonResponse,
    VariantType,
)


class ReviewStatus(str, Enum):
    AI_GENERATED = "ai_generated"
    HUMAN_REVIEWED = "human_reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    RETIRED = "retired"


class SafetyClassification(str, Enum):
    SAFE = "safe"
    REQUIRES_REVIEW = "requires_review"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Lesson:
    id: str
    learner_id: str
    subject: str
    topic: str
    grade: int


__all__ = [
    "DifficultyLevel",
    "LLMProvider",
    "Lesson",
    "LessonCreate",
    "LessonResponse",
    "ReviewStatus",
    "SafetyClassification",
    "VariantType",
]
