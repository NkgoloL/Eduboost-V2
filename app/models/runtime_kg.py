"""Runtime knowledge-graph persistence models for PRD-2.

These tables move the already-reviewed CAPS/learner KG work out of evidence-only
artifacts and into an application-owned runtime projection.  The models are kept
separate from the Phase 02R authoring/review tables so the runtime path can be
loaded idempotently, feature-flagged, and rolled back to legacy behaviour.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


class RuntimeKGGraphLoad(Base):
    """A named, idempotent runtime KG load."""

    __tablename__ = "runtime_kg_graph_loads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    graph_version: Mapped[str] = mapped_column(String(120), nullable=False)
    curriculum_code: Mapped[str] = mapped_column(String(40), nullable=False, default="CAPS")
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_code: Mapped[str] = mapped_column(String(80), nullable=False)
    source_ref: Mapped[str] = mapped_column(Text, nullable=False)
    source_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    node_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    edge_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="staged")
    loaded_by: Mapped[str] = mapped_column(String(120), nullable=False)
    loaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    nodes: Mapped[list["RuntimeKGNode"]] = relationship("RuntimeKGNode", back_populates="graph_load", cascade="all, delete-orphan")
    edges: Mapped[list["RuntimeKGEdge"]] = relationship("RuntimeKGEdge", back_populates="graph_load", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("graph_version", name="uq_runtime_kg_graph_loads_version"),
        CheckConstraint("grade >= 0 AND grade <= 12", name="ck_runtime_kg_graph_loads_grade"),
        CheckConstraint("node_count >= 0", name="ck_runtime_kg_graph_loads_node_count"),
        CheckConstraint("edge_count >= 0", name="ck_runtime_kg_graph_loads_edge_count"),
        CheckConstraint("status IN ('staged','active','superseded','withdrawn')", name="ck_runtime_kg_graph_loads_status"),
        CheckConstraint("length(source_sha256) = 64", name="ck_runtime_kg_graph_loads_sha256"),
        Index("ix_runtime_kg_graph_loads_scope_status", "curriculum_code", "grade", "subject_code", "status"),
    )


class RuntimeKGNode(Base):
    """Runtime query node derived from reviewed CAPS graph mappings."""

    __tablename__ = "runtime_kg_nodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    graph_load_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("runtime_kg_graph_loads.id", ondelete="CASCADE"), nullable=False)
    stable_code: Mapped[str] = mapped_column(String(180), nullable=False)
    node_type: Mapped[str] = mapped_column(String(80), nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    curriculum_code: Mapped[str] = mapped_column(String(40), nullable=False, default="CAPS")
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_code: Mapped[str] = mapped_column(String(80), nullable=False)
    strand: Mapped[str | None] = mapped_column(String(180), nullable=True)
    topic: Mapped[str | None] = mapped_column(String(240), nullable=True)
    mastery_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    properties_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    graph_load: Mapped[RuntimeKGGraphLoad] = relationship("RuntimeKGGraphLoad", back_populates="nodes")

    __table_args__ = (
        UniqueConstraint("graph_load_id", "stable_code", name="uq_runtime_kg_nodes_load_stable_code"),
        CheckConstraint("grade >= 0 AND grade <= 12", name="ck_runtime_kg_nodes_grade"),
        CheckConstraint("mastery_weight >= 0", name="ck_runtime_kg_nodes_mastery_weight"),
        Index("ix_runtime_kg_nodes_scope", "curriculum_code", "grade", "subject_code"),
        Index("ix_runtime_kg_nodes_stable_code", "stable_code"),
    )


class RuntimeKGEdge(Base):
    """Runtime relationship between graph nodes."""

    __tablename__ = "runtime_kg_edges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    graph_load_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("runtime_kg_graph_loads.id", ondelete="CASCADE"), nullable=False)
    from_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("runtime_kg_nodes.id", ondelete="CASCADE"), nullable=False)
    to_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("runtime_kg_nodes.id", ondelete="CASCADE"), nullable=False)
    source_node_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("runtime_kg_nodes.id", ondelete="CASCADE"), nullable=True)
    target_node_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("runtime_kg_nodes.id", ondelete="CASCADE"), nullable=True)
    edge_type: Mapped[str] = mapped_column(String(60), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    properties_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    graph_load: Mapped[RuntimeKGGraphLoad] = relationship("RuntimeKGGraphLoad", back_populates="edges")

    __table_args__ = (
        UniqueConstraint("graph_load_id", "from_node_id", "to_node_id", "edge_type", name="uq_runtime_kg_edges_load_pair_type"),
        CheckConstraint("from_node_id <> to_node_id", name="ck_runtime_kg_edges_distinct_nodes"),
        CheckConstraint("weight >= 0", name="ck_runtime_kg_edges_weight"),
        Index("ix_runtime_kg_edges_from", "from_node_id", "edge_type"),
        Index("ix_runtime_kg_edges_to", "to_node_id", "edge_type"),
    )


class LearnerKGNodeState(Base):
    """Learner mastery state for a runtime graph node."""

    __tablename__ = "learner_kg_node_states"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    learner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    graph_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("runtime_kg_nodes.id", ondelete="CASCADE"), nullable=False)
    mastery_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gap_open: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_evidence_source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (
        UniqueConstraint("learner_id", "graph_node_id", name="uq_learner_kg_node_states_learner_node"),
        CheckConstraint("mastery_score >= 0 AND mastery_score <= 1", name="ck_learner_kg_node_states_mastery"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_learner_kg_node_states_confidence"),
        CheckConstraint("evidence_count >= 0", name="ck_learner_kg_node_states_evidence_count"),
        Index("ix_learner_kg_node_states_gap", "learner_id", "gap_open", "mastery_score"),
    )


class RuntimeKGEvent(Base):
    """Append-only audit trail for runtime KG load/projection activity."""

    __tablename__ = "runtime_kg_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    learner_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    graph_load_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("runtime_kg_graph_loads.id", ondelete="SET NULL"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source: Mapped[str] = mapped_column(String(120), nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("event_type IN ('graph_loaded','graph_activated','learner_projection_updated','rollback_to_legacy')", name="ck_runtime_kg_events_type"),
        Index("ix_runtime_kg_events_created", "created_at"),
    )
