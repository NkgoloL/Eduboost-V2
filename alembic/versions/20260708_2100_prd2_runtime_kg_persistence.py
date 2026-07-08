"""PRD-2 runtime KG persistence tables.

Revision ID: 20260708_2100_prd2_runtime_kg
Revises: 20260622_1200_phase02r_gate2r4
Create Date: 2026-07-08 21:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260708_2100_prd2_runtime_kg"
down_revision = "20260622_1200_phase02r_gate2r4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "runtime_kg_graph_loads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("graph_version", sa.String(length=120), nullable=False),
        sa.Column("curriculum_code", sa.String(length=40), nullable=False, server_default="CAPS"),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("subject_code", sa.String(length=80), nullable=False),
        sa.Column("source_ref", sa.Text(), nullable=False),
        sa.Column("source_sha256", sa.String(length=64), nullable=False),
        sa.Column("node_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("edge_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="staged"),
        sa.Column("loaded_by", sa.String(length=120), nullable=False),
        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("superseded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.CheckConstraint("grade >= 0 AND grade <= 12", name="ck_runtime_kg_graph_loads_grade"),
        sa.CheckConstraint("node_count >= 0", name="ck_runtime_kg_graph_loads_node_count"),
        sa.CheckConstraint("edge_count >= 0", name="ck_runtime_kg_graph_loads_edge_count"),
        sa.CheckConstraint("status IN ('staged','active','superseded','withdrawn')", name="ck_runtime_kg_graph_loads_status"),
        sa.CheckConstraint("length(source_sha256) = 64", name="ck_runtime_kg_graph_loads_sha256"),
        sa.UniqueConstraint("graph_version", name="uq_runtime_kg_graph_loads_version"),
    )
    op.create_index("ix_runtime_kg_graph_loads_scope_status", "runtime_kg_graph_loads", ["curriculum_code", "grade", "subject_code", "status"])

    op.create_table(
        "runtime_kg_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("graph_load_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("runtime_kg_graph_loads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stable_code", sa.String(length=180), nullable=False),
        sa.Column("node_type", sa.String(length=80), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("curriculum_code", sa.String(length=40), nullable=False, server_default="CAPS"),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("subject_code", sa.String(length=80), nullable=False),
        sa.Column("strand", sa.String(length=180), nullable=True),
        sa.Column("topic", sa.String(length=240), nullable=True),
        sa.Column("mastery_weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("properties_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("grade >= 0 AND grade <= 12", name="ck_runtime_kg_nodes_grade"),
        sa.CheckConstraint("mastery_weight >= 0", name="ck_runtime_kg_nodes_mastery_weight"),
        sa.UniqueConstraint("graph_load_id", "stable_code", name="uq_runtime_kg_nodes_load_stable_code"),
    )
    op.create_index("ix_runtime_kg_nodes_scope", "runtime_kg_nodes", ["curriculum_code", "grade", "subject_code"])
    op.create_index("ix_runtime_kg_nodes_stable_code", "runtime_kg_nodes", ["stable_code"])

    op.create_table(
        "runtime_kg_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("graph_load_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("runtime_kg_graph_loads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("runtime_kg_nodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("to_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("runtime_kg_nodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("edge_type", sa.String(length=60), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("properties_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("from_node_id <> to_node_id", name="ck_runtime_kg_edges_distinct_nodes"),
        sa.CheckConstraint("weight >= 0", name="ck_runtime_kg_edges_weight"),
        sa.UniqueConstraint("graph_load_id", "from_node_id", "to_node_id", "edge_type", name="uq_runtime_kg_edges_load_pair_type"),
    )
    op.create_index("ix_runtime_kg_edges_from", "runtime_kg_edges", ["from_node_id", "edge_type"])
    op.create_index("ix_runtime_kg_edges_to", "runtime_kg_edges", ["to_node_id", "edge_type"])

    op.create_table(
        "learner_kg_node_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("learner_id", sa.String(length=36), nullable=False),
        sa.Column("graph_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("runtime_kg_nodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mastery_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gap_open", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_evidence_source", sa.String(length=120), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.CheckConstraint("mastery_score >= 0 AND mastery_score <= 1", name="ck_learner_kg_node_states_mastery"),
        sa.CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_learner_kg_node_states_confidence"),
        sa.CheckConstraint("evidence_count >= 0", name="ck_learner_kg_node_states_evidence_count"),
        sa.UniqueConstraint("learner_id", "graph_node_id", name="uq_learner_kg_node_states_learner_node"),
    )
    op.create_index("ix_learner_kg_node_states_learner_id", "learner_kg_node_states", ["learner_id"])
    op.create_index("ix_learner_kg_node_states_gap", "learner_kg_node_states", ["learner_id", "gap_open", "mastery_score"])

    op.create_table(
        "runtime_kg_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("learner_id", sa.String(length=36), nullable=True),
        sa.Column("graph_load_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("runtime_kg_graph_loads.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("source", sa.String(length=120), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("event_type IN ('graph_loaded','graph_activated','learner_projection_updated','rollback_to_legacy')", name="ck_runtime_kg_events_type"),
    )
    op.create_index("ix_runtime_kg_events_learner_id", "runtime_kg_events", ["learner_id"])
    op.create_index("ix_runtime_kg_events_created", "runtime_kg_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_runtime_kg_events_created", table_name="runtime_kg_events")
    op.drop_index("ix_runtime_kg_events_learner_id", table_name="runtime_kg_events")
    op.drop_table("runtime_kg_events")
    op.drop_index("ix_learner_kg_node_states_gap", table_name="learner_kg_node_states")
    op.drop_index("ix_learner_kg_node_states_learner_id", table_name="learner_kg_node_states")
    op.drop_table("learner_kg_node_states")
    op.drop_index("ix_runtime_kg_edges_to", table_name="runtime_kg_edges")
    op.drop_index("ix_runtime_kg_edges_from", table_name="runtime_kg_edges")
    op.drop_table("runtime_kg_edges")
    op.drop_index("ix_runtime_kg_nodes_stable_code", table_name="runtime_kg_nodes")
    op.drop_index("ix_runtime_kg_nodes_scope", table_name="runtime_kg_nodes")
    op.drop_table("runtime_kg_nodes")
    op.drop_index("ix_runtime_kg_graph_loads_scope_status", table_name="runtime_kg_graph_loads")
    op.drop_table("runtime_kg_graph_loads")
