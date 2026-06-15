"""Strict API contracts for the Phase 5 learner tutor."""
from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class TutorSessionCreate(StrictModel):
    learner_id: str = Field(min_length=1, max_length=80)
    lesson_id: str = Field(min_length=1, max_length=80)
    language: str = Field(default="en", pattern=r"^[a-z]{2}$")


class TutorQuestion(StrictModel):
    text: str = Field(min_length=2, max_length=600)
    client_message_id: str = Field(min_length=8, max_length=80, pattern=r"^[A-Za-z0-9._:-]+$")


class TutorMessageView(StrictModel):
    message_id: UUID
    role: Literal["learner", "assistant", "system"]
    content: str
    safety_status: str
    quality_score: float | None = None
    provider: str | None = None
    created_at: datetime


class TutorSessionView(StrictModel):
    session_id: UUID
    learner_id: str
    lesson_id: str
    language: str
    status: str
    message_count: int
    escalation_count: int
    created_at: datetime
    last_activity_at: datetime
    messages: list[TutorMessageView] = Field(default_factory=list)


class TutorReply(StrictModel):
    session_id: UUID
    learner_message: TutorMessageView
    assistant_message: TutorMessageView
    fallback: bool = False
    escalation_created: bool = False


class TutorCancelResponse(StrictModel):
    session_id: UUID
    status: Literal["cancelled"]
