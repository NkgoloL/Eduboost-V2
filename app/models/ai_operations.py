"""Phase 6 durable AI usage, reservation, and budget accounting models."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _now() -> datetime:
    return datetime.now(UTC)


class AIBudgetCounter(Base):
    """Durable token/cost totals for one scope and accounting period."""

    __tablename__ = "ai_budget_counters"

    scope_type: Mapped[str] = mapped_column(String(16), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    period_key: Mapped[str] = mapped_column(String(16), primary_key=True)
    used_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    reserved_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    used_cost_usd: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False, default=Decimal("0"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    __table_args__ = (
        CheckConstraint("scope_type IN ('user','tenant','global')", name="ck_ai_budget_counter_scope_type"),
        CheckConstraint("used_tokens >= 0 AND reserved_tokens >= 0", name="ck_ai_budget_counter_tokens_nonnegative"),
        CheckConstraint("used_cost_usd >= 0", name="ck_ai_budget_counter_cost_nonnegative"),
        Index("ix_ai_budget_counters_period", "period_key", "scope_type"),
    )


class AIUsageReservation(Base):
    """Pre-call reservation that prevents concurrent budget overspend."""

    __tablename__ = "ai_usage_reservations"

    reservation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False, unique=True)
    user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False)
    purpose: Mapped[str] = mapped_column(String(64), nullable=False)
    estimated_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    failure_reason: Mapped[str | None] = mapped_column(String(96), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    reserved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("estimated_tokens > 0", name="ck_ai_usage_reservation_estimate_positive"),
        CheckConstraint("status IN ('pending','finalized','cancelled','expired')", name="ck_ai_usage_reservation_status"),
        Index("ix_ai_usage_reservations_status_expires", "status", "expires_at"),
        Index("ix_ai_usage_reservations_tenant_created", "tenant_id", "reserved_at"),
    )


class AIUsageEvent(Base):
    """Append-only source of truth for completed AI operations."""

    __tablename__ = "ai_usage_events"

    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_usage_reservations.reservation_id", ondelete="RESTRICT"),
        nullable=False,
    )
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False, unique=True)
    user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False)
    purpose: Mapped[str] = mapped_column(String(64), nullable=False)
    provider: Mapped[str] = mapped_column(String(48), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    total_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False)
    estimated_cost_usd: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False, default=Decimal("0"))
    outcome: Mapped[str] = mapped_column(String(24), nullable=False, default="success")
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)

    __table_args__ = (
        CheckConstraint("prompt_tokens >= 0 AND completion_tokens >= 0 AND total_tokens >= 0", name="ck_ai_usage_event_tokens"),
        CheckConstraint("estimated_cost_usd >= 0", name="ck_ai_usage_event_cost"),
        CheckConstraint("outcome IN ('success','fallback','blocked','error')", name="ck_ai_usage_event_outcome"),
        UniqueConstraint("reservation_id", name="uq_ai_usage_event_reservation"),
        Index("ix_ai_usage_events_tenant_created", "tenant_id", "created_at"),
        Index("ix_ai_usage_events_provider_created", "provider", "created_at"),
        Index("ix_ai_usage_events_purpose_created", "purpose", "created_at"),
    )
