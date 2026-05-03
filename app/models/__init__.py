"""
EduBoost V2 — Domain Layer ORM Models
All SQLAlchemy models live here. This layer has ZERO dependency on FastAPI
HTTP objects, LLM clients, or any infrastructure code.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(UTC)


# ── Enums ─────────────────────────────────────────────────────────────────────


class UserRole(StrEnum):
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"


class SubscriptionTier(StrEnum):
    FREE = "free"
    PREMIUM = "premium"


class ArchetypeLabel(StrEnum):
    KETER = "Keter"
    CHOKMAH = "Chokmah"
    BINAH = "Binah"
    CHESED = "Chesed"
    GEVURAH = "Gevurah"
    TIFERET = "Tiferet"
    NETZACH = "Netzach"
    HOD = "Hod"
    YESOD = "Yesod"
    MALKUTH = "Malkuth"


class Language(StrEnum):
    ENGLISH = "en"
    ISIZULU = "zu"
    AFRIKAANS = "af"
    ISIXHOSA = "xh"


# ── Guardian (Parent / Teacher) ───────────────────────────────────────────────


class Guardian(Base):
    __tablename__ = "guardians"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.PARENT)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    learners: Mapped[list[LearnerProfile]] = relationship("LearnerProfile", back_populates="guardian")
    consents: Mapped[list[ParentalConsent]] = relationship("ParentalConsent", back_populates="guardian")


# ── Learner Profile ───────────────────────────────────────────────────────────


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    pseudonym_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=_uuid, index=True)
    guardian_id: Mapped[str] = mapped_column(ForeignKey("guardians.id", ondelete="CASCADE"), nullable=False)
    display_name: Mapped[str] = mapped_column(String(80), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=GradeR, 1-7
    language: Mapped[Language] = mapped_column(Enum(Language), default=Language.ENGLISH)
    archetype: Mapped[ArchetypeLabel | None] = mapped_column(Enum(ArchetypeLabel), nullable=True)
    theta: Mapped[float] = mapped_column(Float, default=0.0)       # IRT ability estimate
    xp: Mapped[int] = mapped_column(Integer, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_active: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)  # soft-delete (POPIA)
    deletion_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    guardian: Mapped[Guardian] = relationship("Guardian", back_populates="learners")
    consents: Mapped[list[ParentalConsent]] = relationship("ParentalConsent", back_populates="learner")
    knowledge_gaps: Mapped[list[KnowledgeGap]] = relationship("KnowledgeGap", back_populates="learner")
    diagnostic_sessions: Mapped[list[DiagnosticSession]] = relationship("DiagnosticSession", back_populates="learner")
    lessons: Mapped[list[Lesson]] = relationship("Lesson", back_populates="learner")

    __table_args__ = (Index("ix_learner_guardian_grade", "guardian_id", "grade"),)


Learner = LearnerProfile


# ── Parental Consent (POPIA) ──────────────────────────────────────────────────


class ParentalConsent(Base):
    __tablename__ = "parental_consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    guardian_id: Mapped[str] = mapped_column(ForeignKey("guardians.id", ondelete="CASCADE"), nullable=False)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC) + timedelta(days=365),
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_address_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    guardian: Mapped[Guardian] = relationship("Guardian", back_populates="consents")
    learner: Mapped[LearnerProfile] = relationship("LearnerProfile", back_populates="consents")

    @property
    def is_active(self) -> bool:
        now = datetime.now(UTC)
        return self.revoked_at is None and self.expires_at > now

    __table_args__ = (UniqueConstraint("guardian_id", "learner_id", name="uq_consent_guardian_learner"),)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    __table_args__ = (
        Index("idx_audit_events_actor", "actor_id"),
        Index("idx_audit_events_type", "event_type"),
        Index("idx_audit_events_ts", "created_at"),
    )


# ── IRT Item Bank ─────────────────────────────────────────────────────────────


class IRTItem(Base):
    __tablename__ = "irt_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject: Mapped[str] = mapped_column(String(60), nullable=False)
    topic: Mapped[str] = mapped_column(String(120), nullable=False)
    language: Mapped[Language] = mapped_column(Enum(Language), default=Language.ENGLISH)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict] = mapped_column(JSONB, nullable=False)      # {A: ..., B: ..., C: ..., D: ...}
    correct_option: Mapped[str] = mapped_column(String(1), nullable=False)
    a_param: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)   # discrimination
    b_param: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)   # difficulty
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    __table_args__ = (Index("ix_irt_grade_subject", "grade", "subject"),)


# ── Diagnostic Session ────────────────────────────────────────────────────────


class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False)
    responses: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)  # {item_id: bool}
    theta_before: Mapped[float] = mapped_column(Float, default=0.0)
    theta_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    learner: Mapped[LearnerProfile] = relationship("LearnerProfile", back_populates="diagnostic_sessions")


# ── Knowledge Gap ─────────────────────────────────────────────────────────────


class KnowledgeGap(Base):
    __tablename__ = "knowledge_gaps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject: Mapped[str] = mapped_column(String(60), nullable=False)
    topic: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[float] = mapped_column(Float, default=1.0)  # 0=mild … 1=critical
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    learner: Mapped[LearnerProfile] = relationship("LearnerProfile", back_populates="knowledge_gaps")


# ── Lesson ────────────────────────────────────────────────────────────────────


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False)
    knowledge_gap_id: Mapped[str | None] = mapped_column(ForeignKey("knowledge_gaps.id"), nullable=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject: Mapped[str] = mapped_column(String(60), nullable=False)
    topic: Mapped[str] = mapped_column(String(120), nullable=False)
    language: Mapped[Language] = mapped_column(Enum(Language), default=Language.ENGLISH)
    archetype: Mapped[ArchetypeLabel | None] = mapped_column(Enum(ArchetypeLabel), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    llm_provider: Mapped[str] = mapped_column(String(30), default="groq")
    served_from_cache: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    learner: Mapped[LearnerProfile] = relationship("LearnerProfile", back_populates="lessons")


# ── Audit Log (append-only, replaces RabbitMQ/Redis Streams) ─────────────────


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    actor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    learner_pseudonym: Mapped[str | None] = mapped_column(String(36), nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    constitutional_outcome: Mapped[str | None] = mapped_column(String(20), nullable=True)  # APPROVED/REJECTED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    __table_args__ = (Index("ix_audit_event_created", "event_type", "created_at"),)


# ── Stripe Webhook Events (idempotency log) ───────────────────────────────────


class StripeWebhookEvent(Base):
    __tablename__ = "stripe_webhook_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    stripe_event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


LessonRecord = Lesson
