"""Pydantic schemas for EduBoost V2 API contracts."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LearnerSummary(BaseModel):
    learner_id: str
    grade: int = Field(ge=0, le=7)
    home_language: str
    overall_mastery: float = Field(ge=0.0, le=1.0)


class AuditLogEntry(BaseModel):
    event_id: str
    learner_id: str | None = None
    event_type: str
    occurred_at: datetime
    payload: dict = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    mode: str
