"""Phase 5 learner-tutor persistence models.

Tutor content is stored only after input/output privacy filtering.  Raw learner
free text is represented by a SHA-256 digest so evidence can prove idempotency
without retaining unredacted personal information.
"""
from __future__ import annotations

import uuid

import sqlalchemy as sa
from datetime import UTC, datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _now() -> datetime:
    return datetime.now(UTC)


class TutorSession(Base):
    __tablename__ = "tutor_sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False)
    lesson_id: Mapped[str] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    created_by: Mapped[str] = mapped_column(String(80), nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")
    context_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    escalation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)

    messages: Mapped[list["TutorMessage"]] = relationship(back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('active','cancelled','escalated','closed')", name="ck_tutor_sessions_status"),
        CheckConstraint("message_count >= 0", name="ck_tutor_sessions_message_count"),
        CheckConstraint("escalation_count >= 0", name="ck_tutor_sessions_escalation_count"),
        Index("ix_tutor_sessions_learner_activity", "learner_id", "last_activity_at"),
        Index("ix_tutor_sessions_lesson", "lesson_id"),
        Index("uq_tutor_sessions_active_lesson", "learner_id", "lesson_id", unique=True, postgresql_where=sa.text("status = 'active'")),
    )


class TutorMessage(Base):
    __tablename__ = "tutor_messages"

    message_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tutor_sessions.session_id", ondelete="CASCADE"), nullable=False
    )
    client_message_id: Mapped[str] = mapped_column(String(80), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    pii_redacted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    safety_status: Mapped[str] = mapped_column(String(24), nullable=False, default="safe")
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    provider: Mapped[str | None] = mapped_column(String(40), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)

    session: Mapped[TutorSession] = relationship(back_populates="messages")

    __table_args__ = (
        UniqueConstraint("session_id", "client_message_id", "role", name="uq_tutor_message_session_client_role"),
        CheckConstraint("role IN ('learner','assistant','system')", name="ck_tutor_messages_role"),
        CheckConstraint("safety_status IN ('safe','redacted','blocked','fallback','escalated')", name="ck_tutor_messages_safety"),
        CheckConstraint("quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)", name="ck_tutor_messages_quality"),
        CheckConstraint("prompt_tokens >= 0 AND completion_tokens >= 0", name="ck_tutor_messages_tokens"),
        Index("ix_tutor_messages_session_created", "session_id", "created_at"),
    )


class TutorEscalation(Base):
    __tablename__ = "tutor_escalations"

    escalation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tutor_sessions.session_id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tutor_messages.message_id", ondelete="SET NULL"), nullable=True
    )
    reason_code: Mapped[str] = mapped_column(String(48), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="open")
    assigned_to: Mapped[str | None] = mapped_column(String(80), nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)

    __table_args__ = (
        CheckConstraint("severity IN ('low','medium','high','critical')", name="ck_tutor_escalations_severity"),
        CheckConstraint("status IN ('open','acknowledged','resolved','dismissed')", name="ck_tutor_escalations_status"),
        Index("ix_tutor_escalations_status_created", "status", "created_at"),
        Index("ix_tutor_escalations_session", "session_id"),
    )
