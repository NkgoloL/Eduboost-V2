"""Longitudinal Educational Validation ORM models (LEV-WS03).

Provides append-only persistence for learner interaction events, mastery state transitions
with cryptographic SHA-256 state hashing, and analytical validation run ledger.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class LEVInteractionEvent(Base):
    __tablename__ = "lev_interaction_events"

    event_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    learner_pseudonym: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    concept_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    item_id: Mapped[str] = mapped_column(String(128), nullable=False)
    item_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0")
    graph_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")
    model_version: Mapped[str] = mapped_column(String(32), nullable=False, default="lev-1.0")
    consent_state: Mapped[str] = mapped_column(String(64), nullable=False, default="consented")
    first_attempt_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    hint_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    response_latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    teacher_assistance: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    evidence_type: Mapped[str] = mapped_column(String(32), nullable=False, default="synthetic_fixture")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("ix_lev_events_learner_concept", "learner_pseudonym", "concept_id"),
        Index("ix_lev_events_occurred", "occurred_at"),
        CheckConstraint(
            "evidence_type IN ('synthetic_fixture', 'empirical_field')",
            name="ck_lev_interaction_events_evidence_type",
        ),
    )


class LEVMasteryStateTransition(Base):
    __tablename__ = "lev_mastery_state_transitions"

    transition_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    learner_pseudonym: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    concept_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    pre_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    post_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    evidence_event_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False, default="lev-1.0")
    graph_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")
    update_rationale: Mapped[str] = mapped_column(Text, nullable=False, default="")
    state_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(32), nullable=False, default="synthetic_fixture")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("ix_lev_transitions_learner_concept", "learner_pseudonym", "concept_id"),
        CheckConstraint(
            "evidence_type IN ('synthetic_fixture', 'empirical_field')",
            name="ck_lev_transitions_evidence_type",
        ),
    )


class LEVValidationRun(Base):
    __tablename__ = "lev_validation_runs"

    run_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    run_type: Mapped[str] = mapped_column(String(64), nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(32), nullable=False, default="synthetic_fixture")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    manifest_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("ix_lev_validation_runs_type_status", "run_type", "status"),
        CheckConstraint(
            "evidence_type IN ('synthetic_fixture', 'empirical_field')",
            name="ck_lev_validation_runs_evidence_type",
        ),
    )
