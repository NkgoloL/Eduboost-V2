"""
EduBoost V2 — Domain Layer ORM Models
All SQLAlchemy models live here. This layer has ZERO dependency on FastAPI
HTTP objects, LLM clients, or any infrastructure code.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
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


def _enum_values(enum_cls):
    return [member.value for member in enum_cls]


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


class ConsentState(StrEnum):
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    RENEWAL_REQUIRED = "renewal_required"


class ItemReviewStatus(StrEnum):
    DRAFT = "draft"
    AI_GENERATED = "ai_generated"
    HUMAN_REVIEWED = "human_reviewed"
    APPROVED = "approved"
    RETIRED = "retired"


# ── Guardian (Parent / Teacher) ───────────────────────────────────────────────


class Guardian(Base):
    __tablename__ = "guardians"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, values_callable=_enum_values), nullable=False, default=UserRole.PARENT)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier, values_callable=_enum_values), nullable=False, default=SubscriptionTier.FREE
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (
        Index("ix_guardians_created_at", "created_at"),
        Index("ix_guardians_stripe_customer_id", "stripe_customer_id", postgresql_where=sa.text("stripe_customer_id IS NOT NULL")),
        Index("ix_guardians_stripe_subscription_id", "stripe_subscription_id", postgresql_where=sa.text("stripe_subscription_id IS NOT NULL")),
        Index(
            "ix_guardians_active_subscription",
            "subscription_tier",
            "stripe_subscription_id",
            postgresql_where=sa.text(
                "is_active IS TRUE AND stripe_subscription_id IS NOT NULL "
                "AND lower(subscription_tier::text) = 'premium'"
            ),
        ),
    )

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
    language: Mapped[Language] = mapped_column(Enum(Language, values_callable=_enum_values), default=Language.ENGLISH)
    archetype: Mapped[ArchetypeLabel | None] = mapped_column(Enum(ArchetypeLabel, values_callable=_enum_values), nullable=True)
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
    mastery_records: Mapped[list[SubjectMastery]] = relationship("SubjectMastery", back_populates="learner")
    diagnostic_sessions: Mapped[list[DiagnosticSession]] = relationship("DiagnosticSession", back_populates="learner")
    lessons: Mapped[list[Lesson]] = relationship("Lesson", back_populates="learner")

    __table_args__ = (
        CheckConstraint("grade >= 0 AND grade <= 12", name="ck_learner_profiles_grade_range"),
        CheckConstraint("xp >= 0", name="ck_learner_profiles_xp_non_negative"),
        CheckConstraint("streak_days >= 0", name="ck_learner_profiles_streak_non_negative"),
        Index("ix_learner_guardian_grade", "guardian_id", "grade"),
        Index("ix_learner_profiles_created_at", "created_at"),
        Index("ix_learner_profiles_last_active", "last_active"),
    )


Learner = LearnerProfile


# ── Parental Consent (POPIA) ──────────────────────────────────────────────────


class ParentalConsent(Base):
    __tablename__ = "parental_consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    guardian_id: Mapped[str] = mapped_column(ForeignKey("guardians.id", ondelete="CASCADE"), nullable=False)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    status: Mapped[ConsentState] = mapped_column(Enum(ConsentState, values_callable=_enum_values), nullable=False, default=ConsentState.GRANTED)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC) + timedelta(days=365),
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_address_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    guardian: Mapped[Guardian] = relationship("Guardian", back_populates="consents")
    learner: Mapped[LearnerProfile] = relationship("LearnerProfile", back_populates="consents")

    @property
    def is_active(self) -> bool:
        now = datetime.now(UTC)
        return (
            self.revoked_at is None
            and self.expires_at > now
            and self.status in {ConsentState.GRANTED, ConsentState.RENEWAL_REQUIRED}
        )

    __table_args__ = (
        UniqueConstraint("guardian_id", "learner_id", name="uq_consent_guardian_learner"),
        CheckConstraint("expires_at > granted_at", name="ck_parental_consents_expiry_after_grant"),
        CheckConstraint("revoked_at IS NULL OR revoked_at >= granted_at", name="ck_parental_consents_revoked_after_grant"),
        Index(
            "ix_active_parental_consents",
            "learner_id",
            postgresql_where=sa.text("revoked_at IS NULL AND expires_at > CURRENT_TIMESTAMP"),
        ),
        Index("ix_parental_consents_status", "status"),
        Index("ix_parental_consents_guardian_learner_status", "guardian_id", "learner_id", "status"),
        Index(
            "ix_parental_consents_active_status",
            "learner_id",
            "guardian_id",
            postgresql_where=sa.text(
                "revoked_at IS NULL AND expires_at > CURRENT_TIMESTAMP "
                "AND status::text IN ('GRANTED', 'RENEWAL_REQUIRED', 'granted', 'renewal_required')"
            ),
        ),
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    previous_event_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    hmac_signature: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    __table_args__ = (
        CheckConstraint("length(btrim(event_type)) > 0", name="ck_audit_events_event_type_not_blank"),
        CheckConstraint("event_hash = '' OR event_hash ~ '^[0-9a-f]{64}$'", name="ck_audit_events_hash_hex64_or_bootstrap"),
        CheckConstraint("hmac_signature = '' OR hmac_signature ~ '^[0-9a-f]{64}$'", name="ck_audit_events_hmac_hex64_or_bootstrap"),
        CheckConstraint("previous_event_hash IS NULL OR previous_event_hash ~ '^[0-9a-f]{64}$'", name="ck_audit_events_previous_hash_hex64"),
        Index("idx_audit_events_actor", "actor_id"),
        Index("idx_audit_events_type", "event_type"),
        Index("idx_audit_events_ts", "created_at"),
        Index("idx_audit_events_hash", "event_hash"),
    )


# ── IRT Item Bank ─────────────────────────────────────────────────────────────


class IRTItem(Base):
    __tablename__ = "irt_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject: Mapped[str] = mapped_column(String(60), nullable=False)
    topic: Mapped[str] = mapped_column(String(120), nullable=False)
    skill: Mapped[str] = mapped_column(String(120), nullable=False, default="general")
    caps_reference: Mapped[str | None] = mapped_column(String(220), nullable=True)
    language: Mapped[Language] = mapped_column(Enum(Language, values_callable=_enum_values), default=Language.ENGLISH)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict] = mapped_column(JSONB, nullable=False)      # {A: ..., B: ..., C: ..., D: ...}
    correct_option: Mapped[str] = mapped_column(String(1), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False, default="Review the worked solution and compare it with the selected option.")
    misconception_tag: Mapped[str | None] = mapped_column(String(120), nullable=True)
    review_status: Mapped[ItemReviewStatus] = mapped_column(
        Enum(ItemReviewStatus, values_callable=_enum_values), nullable=False, default=ItemReviewStatus.AI_GENERATED
    )
    a_param: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)   # discrimination
    b_param: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)   # difficulty
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    __table_args__ = (
        CheckConstraint("grade >= 0 AND grade <= 12", name="ck_irt_items_grade_range"),
        CheckConstraint("correct_option IN ('A', 'B', 'C', 'D')", name="ck_irt_items_correct_option"),
        CheckConstraint("a_param > 0", name="ck_irt_items_a_param_positive"),
        CheckConstraint("a_param > 0 AND a_param <= 4", name="ck_irt_items_a_param_bounds"),
        CheckConstraint("b_param >= -4 AND b_param <= 4", name="ck_irt_items_b_param_bounds"),
        CheckConstraint("length(btrim(skill)) > 0", name="ck_irt_items_skill_not_blank"),
        CheckConstraint("length(btrim(explanation)) > 0", name="ck_irt_items_explanation_not_blank"),
        Index("ix_irt_grade_subject", "grade", "subject"),
    )


# ── Diagnostic Session ────────────────────────────────────────────────────────


class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False)
    responses: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)  # {item_id: bool}
    theta_before: Mapped[float] = mapped_column(Float, default=0.0)
    theta_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    items_correct: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    learner: Mapped[LearnerProfile] = relationship("LearnerProfile", back_populates="diagnostic_sessions")

    __table_args__ = (
        Index("ix_diagnostic_sessions_created_at", "created_at"),
        Index(
            "ix_diagnostic_sessions_incomplete",
            "learner_id",
            "created_at",
            postgresql_where=sa.text("completed_at IS NULL"),
        ),
    )


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

    __table_args__ = (
        CheckConstraint("severity >= 0 AND severity <= 1", name="ck_knowledge_gaps_severity_range"),
        Index("ix_knowledge_gaps_created_at", "created_at"),
    )

    learner: Mapped[LearnerProfile] = relationship("LearnerProfile", back_populates="knowledge_gaps")


# ── Mastery Tracking ─────────────────────────────────────────────────────────


class SubjectMastery(Base):
    __tablename__ = "subject_mastery"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False)
    subject: Mapped[str] = mapped_column(String(60), nullable=False)
    topic: Mapped[str] = mapped_column(String(120), nullable=False)
    theta: Mapped[float] = mapped_column(Float, default=0.0)       # Topic-level ability
    standard_error: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (
        CheckConstraint("standard_error >= 0", name="ck_subject_mastery_standard_error_non_negative"),
        Index("ix_subject_mastery_learner_subject", "learner_id", "subject"),
        Index("ix_subject_mastery_last_updated", "last_updated"),
    )

    learner: Mapped[LearnerProfile] = relationship("LearnerProfile", back_populates="mastery_records")


# ── Lesson ────────────────────────────────────────────────────────────────────


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False)
    knowledge_gap_id: Mapped[str | None] = mapped_column(ForeignKey("knowledge_gaps.id"), nullable=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject: Mapped[str] = mapped_column(String(60), nullable=False)
    topic: Mapped[str] = mapped_column(String(120), nullable=False)
    language: Mapped[Language] = mapped_column(Enum(Language, values_callable=_enum_values), default=Language.ENGLISH)
    archetype: Mapped[ArchetypeLabel | None] = mapped_column(Enum(ArchetypeLabel, values_callable=_enum_values), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    caps_reference: Mapped[str | None] = mapped_column(String(220), nullable=True)
    alignment_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    trust_label: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    llm_provider: Mapped[str] = mapped_column(String(30), default="groq")
    served_from_cache: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    __table_args__ = (
        CheckConstraint("grade >= 0 AND grade <= 12", name="ck_lessons_grade_range"),
        CheckConstraint("feedback_score IS NULL OR (feedback_score >= 1 AND feedback_score <= 5)", name="ck_lessons_feedback_score_range"),
        CheckConstraint("alignment_confidence >= 0 AND alignment_confidence <= 1", name="ck_lessons_alignment_confidence_range"),
        CheckConstraint("quality_score >= 0 AND quality_score <= 1", name="ck_lessons_quality_score_range"),
        Index("ix_lessons_created_at", "created_at"),
        Index("ix_lessons_caps_reference", "caps_reference"),
    )

    learner: Mapped[LearnerProfile] = relationship("LearnerProfile", back_populates="lessons")


# ── RLHF Feedback and Exports ────────────────────────────────────────────────


class LessonFeedback(Base):
    __tablename__ = "lesson_feedback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id: Mapped[str | None] = mapped_column(ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True)
    learner_pseudonym: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    grade_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language_code: Mapped[str] = mapped_column(String(8), default="en", nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_lesson_feedback_rating_range"),
        Index("ix_feedback_lesson_id", "lesson_id"),
        Index("ix_feedback_exported_at", "exported_at"),
    )


class RLHFExport(Base):
    __tablename__ = "rlhf_exports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    format: Mapped[str] = mapped_column(Text, nullable=False)
    language_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    positive_count: Mapped[int] = mapped_column(Integer, nullable=False)
    negative_count: Mapped[int] = mapped_column(Integer, nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False)
    dataset_json: Mapped[str] = mapped_column(Text, nullable=False)
    exported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)

    __table_args__ = (
        CheckConstraint("positive_count >= 0", name="ck_rlhf_exports_positive_count_non_negative"),
        CheckConstraint("negative_count >= 0", name="ck_rlhf_exports_negative_count_non_negative"),
        CheckConstraint("record_count >= 0", name="ck_rlhf_exports_record_count_non_negative"),
    )


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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (Index("ix_stripe_webhook_processed_at", "processed_at"),)


LessonRecord = Lesson
