"""Lightweight domain entities used by service-level tests and DTO mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class LearnerProfile:
    learner_id: str
    grade: int
    home_language: str = "en"
    overall_mastery: float = 0.0


@dataclass(slots=True)
class AuditLog:
    event_id: str
    learner_id: str | None
    event_type: str
    occurred_at: datetime
    payload: dict[str, Any] = field(default_factory=dict)
