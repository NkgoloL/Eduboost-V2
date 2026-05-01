"""Foundational V2 domain entities.

These dataclasses define the initial domain language requested by the V2
manifest without coupling to FastAPI or third-party LLM clients.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class LearnerProfile:
    learner_id: str
    grade: int
    home_language: str
    overall_mastery: float = 0.0


@dataclass(slots=True)
class Guardian:
    guardian_id: str
    learner_id: str
    relationship: str
    consent_active: bool = False


@dataclass(slots=True)
class KnowledgeGap:
    subject_code: str
    concept: str
    grade_level: int
    severity: float


@dataclass(slots=True)
class Lesson:
    lesson_id: str
    learner_id: str
    subject_code: str
    topic: str
    generated_at: datetime
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AuditLog:
    event_id: str
    learner_id: str | None
    event_type: str
    occurred_at: datetime
    payload: dict[str, Any] = field(default_factory=dict)
