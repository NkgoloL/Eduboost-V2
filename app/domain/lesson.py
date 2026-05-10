from __future__ import annotations

from enum import Enum

from app.modules.lessons.lesson_schema_v1 import (
    DifficultyLevel,
    LLMProvider,
    LessonCreate,
    LessonResponse,
    ReviewStatus as _ReviewStatus,
    SafetyClassification as _SafetyClassification,
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


__all__ = [
    "DifficultyLevel",
    "LLMProvider",
    "LessonCreate",
    "LessonResponse",
    "ReviewStatus",
    "SafetyClassification",
    "VariantType",
]
