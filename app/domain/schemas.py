"""
EduBoost V2 — Pydantic API Schemas
Request/response models. No ORM imports here.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Shared ────────────────────────────────────────────────────────────────────
class OrmBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ── Auth ──────────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str = Field(min_length=2, max_length=120)
    role: Literal["parent", "teacher"] = "parent"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


# ── Learner ───────────────────────────────────────────────────────────────────
class LearnerCreate(BaseModel):
    display_name: str = Field(min_length=2, max_length=80)
    grade: int = Field(ge=0, le=7)
    language: str = "en"


class LearnerResponse(OrmBase):
    id: str
    pseudonym_id: str
    display_name: str
    grade: int
    language: str
    archetype: str | None
    theta: float
    xp: int
    streak_days: int
    created_at: datetime


# ── Lesson ────────────────────────────────────────────────────────────────────
class LessonRequest(BaseModel):
    learner_id: str
    subject: str
    topic: str
    language: str = "en"


class LessonResponse(OrmBase):
    id: str
    grade: int
    subject: str
    topic: str
    language: str
    content: str
    archetype: str | None
    served_from_cache: bool
    created_at: datetime


class LessonFeedback(BaseModel):
    score: int = Field(ge=1, le=5)


# ── Diagnostic ────────────────────────────────────────────────────────────────
class DiagnosticAnswer(BaseModel):
    item_id: str
    selected_option: str  # "A" | "B" | "C" | "D"


class DiagnosticSubmit(BaseModel):
    learner_id: str
    answers: list[DiagnosticAnswer]


class DiagnosticResult(BaseModel):
    session_id: str
    theta_before: float
    theta_after: float
    gaps_identified: list[str]


# ── Onboarding (Ether cold-start) ─────────────────────────────────────────────
class OnboardingAnswer(BaseModel):
    question_id: int = Field(ge=1, le=5)
    answer: str


class OnboardingSubmit(BaseModel):
    learner_id: str
    answers: list[OnboardingAnswer]


class OnboardingResult(BaseModel):
    learner_id: str
    archetype: str
    description: str


# ── Parent Portal ─────────────────────────────────────────────────────────────
class ProgressSummary(BaseModel):
    learner_id: str
    display_name: str
    grade: int
    theta: float
    xp: int
    streak_days: int
    lessons_completed: int
    active_gaps: int
    ai_summary: str


class ConsentStatus(OrmBase):
    is_active: bool
    policy_version: str
    granted_at: datetime
    expires_at: datetime


# ── Stripe ────────────────────────────────────────────────────────────────────
class CheckoutSessionResponse(BaseModel):
    checkout_url: str


# ── Quota ─────────────────────────────────────────────────────────────────────
class QuotaStatus(BaseModel):
    used_today: int
    daily_limit: int
    tier: str


class AuditLogEntry(BaseModel):
    event_id: str
    learner_id: str | None = None
    event_type: str
    occurred_at: datetime
    payload: dict = Field(default_factory=dict)
