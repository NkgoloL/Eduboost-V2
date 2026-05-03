"""
EduBoost SA — ORM Models
All SQLAlchemy 2.0 models managed by Alembic.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, Numeric,
    String, Text, UniqueConstraint, Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _now() -> datetime:
    return datetime.now(UTC)


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


# ── Guardian (Parent / Carer) ─────────────────────────────────────────────────

class Guardian(Base):
    __tablename__ = "guardians"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    email_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email_encrypted: Mapped[str] = mapped_column(Text, nullable=False)  # Fernet-encrypted
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    phone_encrypted: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_token: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    learners: Mapped[list[Learner]] = relationship("Learner", back_populates="guardian")
    consents: Mapped[list[ParentalConsent]] = relationship("ParentalConsent", back_populates="guardian")

    def __repr__(self) -> str:
        return f"<Guardian {self.id}>"


# ── Learner ───────────────────────────────────────────────────────────────────

class Grade(StrEnum):
    R = "R"; G1 = "1"; G2 = "2"; G3 = "3"; G4 = "4"; G5 = "5"; G6 = "6"; G7 = "7"


class Language(StrEnum):
    ENGLISH = "en"; ZULU = "zu"; XHOSA = "xh"; AFRIKAANS = "af"
    SOTHO = "st"; TSWANA = "tn"; VENDA = "ve"; TSONGA = "ts"
    NDEBELE = "nr"; SWATI = "ss"; PEDI = "nso"


class Learner(Base):
    __tablename__ = "learners"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    pseudonym_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    guardian_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("guardians.id"), nullable=False)
    first_name_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    grade: Mapped[str] = mapped_column(String(4), nullable=False)
    home_language: Mapped[str] = mapped_column(String(8), nullable=False, default=Language.ENGLISH)
    preferred_language: Mapped[str] = mapped_column(String(8), nullable=False, default=Language.ENGLISH)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_erased: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # POPIA erasure
    erased_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    guardian: Mapped[Guardian] = relationship("Guardian", back_populates="learners")
    consents: Mapped[list[ParentalConsent]] = relationship("ParentalConsent", back_populates="learner")
    diagnostic_sessions: Mapped[list[DiagnosticSession]] = relationship("DiagnosticSession", back_populates="learner")
    lessons: Mapped[list[Lesson]] = relationship("Lesson", back_populates="learner")
    study_plans: Mapped[list[StudyPlan]] = relationship("StudyPlan", back_populates="learner")

    def __repr__(self) -> str:
        return f"<Learner {self.id} grade={self.grade}>"


# ── Parental Consent ─────────────────────────────────────────────────────────

class ParentalConsent(Base):
    __tablename__ = "parental_consents"
    __table_args__ = (
        Index("ix_consent_learner_active", "learner_id", "is_active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    learner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"), nullable=False)
    guardian_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("guardians.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)  # Annual renewal
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revocation_reason: Mapped[str | None] = mapped_column(Text)
    consent_version: Mapped[str] = mapped_column(String(16), nullable=False, default="1.0")
    ip_address: Mapped[str | None] = mapped_column(String(45))  # IPv6 max length
    user_agent: Mapped[str | None] = mapped_column(Text)

    learner: Mapped[Learner] = relationship("Learner", back_populates="consents")
    guardian: Mapped[Guardian] = relationship("Guardian", back_populates="consents")

    @property
    def is_expired(self) -> bool:
        return datetime.now(UTC) > self.expires_at

    def __repr__(self) -> str:
        return f"<ParentalConsent learner={self.learner_id} active={self.is_active}>"


# ── Diagnostic Session ────────────────────────────────────────────────────────

class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    learner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"), nullable=False)
    subject: Mapped[str] = mapped_column(String(64), nullable=False)
    grade: Mapped[str] = mapped_column(String(4), nullable=False)
    ability_estimate: Mapped[float | None] = mapped_column(Numeric(6, 4))
    ability_std_error: Mapped[float | None] = mapped_column(Numeric(6, 4))
    items_administered: Mapped[int] = mapped_column(Integer, default=0)
    responses: Mapped[dict | None] = mapped_column(JSONB)  # {item_id: bool}
    item_parameters: Mapped[dict | None] = mapped_column(JSONB)  # IRT a, b, c params
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    learner: Mapped[Learner] = relationship("Learner", back_populates="diagnostic_sessions")
    items: Mapped[list[DiagnosticItem]] = relationship("DiagnosticItem", back_populates="session")

    def __repr__(self) -> str:
        return f"<DiagnosticSession {self.id} subject={self.subject}>"


class DiagnosticItem(Base):
    __tablename__ = "diagnostic_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("diagnostic_sessions.id"))
    item_id: Mapped[str] = mapped_column(String(128), nullable=False)
    difficulty: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    discrimination: Mapped[float] = mapped_column(Numeric(6, 4), default=1.0)
    response: Mapped[bool | None] = mapped_column(Boolean)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    administered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    session: Mapped[DiagnosticSession] = relationship("DiagnosticSession", back_populates="items")


# ── Lesson ────────────────────────────────────────────────────────────────────

class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    learner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"), nullable=False)
    subject: Mapped[str] = mapped_column(String(64), nullable=False)
    grade: Mapped[str] = mapped_column(String(4), nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False)
    topic: Mapped[str] = mapped_column(String(256), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    llm_provider: Mapped[str] = mapped_column(String(32), nullable=False)  # groq|anthropic
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    ability_level: Mapped[float | None] = mapped_column(Numeric(6, 4))  # IRT theta at generation time
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    learner: Mapped[Learner] = relationship("Learner", back_populates="lessons")
    feedback: Mapped[list[LessonFeedback]] = relationship("LessonFeedback", back_populates="lesson")

    def __repr__(self) -> str:
        return f"<Lesson {self.id} {self.subject}/{self.grade}>"


class LessonFeedback(Base):
    """RLHF feedback on generated lessons."""
    __tablename__ = "lesson_feedback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    lesson_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    learner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    was_helpful: Mapped[bool | None] = mapped_column(Boolean)
    was_too_hard: Mapped[bool | None] = mapped_column(Boolean)
    was_too_easy: Mapped[bool | None] = mapped_column(Boolean)
    free_text_encrypted: Mapped[str | None] = mapped_column(Text)  # Encrypted free-text
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    lesson: Mapped[Lesson] = relationship("Lesson", back_populates="feedback")


# ── Study Plan ────────────────────────────────────────────────────────────────

class StudyPlan(Base):
    __tablename__ = "study_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    learner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"), nullable=False)
    diagnostic_session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("diagnostic_sessions.id"))
    plan_data: Mapped[dict] = mapped_column(JSONB, nullable=False)  # Structured weekly plan
    week_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    learner: Mapped[Learner] = relationship("Learner", back_populates="study_plans")

    def __repr__(self) -> str:
        return f"<StudyPlan {self.id} learner={self.learner_id}>"


# ── Audit Log ─────────────────────────────────────────────────────────────────

class AuditLog(Base):
    """
    POPIA-compliant audit trail.
    Replaces the V1 RabbitMQ/fourth_estate.py approach.
    Written in the same DB transaction as the audited operation.
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_learner_id", "learner_id"),
        Index("ix_audit_action", "action"),
        Index("ix_audit_occurred_at", "occurred_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(128))      # Guardian/admin UUID
    learner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)
    resource_type: Mapped[str | None] = mapped_column(String(64))
    resource_id: Mapped[str | None] = mapped_column(String(128))
    metadata_json: Mapped[str | None] = mapped_column("metadata", Text)  # JSON, PII-stripped
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} at {self.occurred_at}>"
