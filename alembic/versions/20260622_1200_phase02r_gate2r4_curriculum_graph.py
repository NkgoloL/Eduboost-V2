"""Phase 02R Gate 2R.4 curriculum graph and reviewed mappings.

Revision ID: 20260622_1200_phase02r_gate2r4
Revises: 20260618_1200_phase02r_grounding
Create Date: 2026-06-22 12:00:00+02:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260622_1200_phase02r_gate2r4"
down_revision = "20260618_1200_phase02r_grounding"
branch_labels = None
depends_on = None


def _uuid_pk(name: str) -> sa.Column:
    return sa.Column(name, postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))


def _created() -> sa.Column:
    return sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())


def _jsonb(name: str, default: str = "'{}'::jsonb") -> sa.Column:
    return sa.Column(name, postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text(default))


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "curriculum_nodes",
        _uuid_pk("curriculum_node_id"),
        sa.Column("curriculum_code", sa.String(40), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("subject_code", sa.String(80), nullable=False),
        sa.Column("stable_code", sa.String(180), nullable=False),
        sa.Column("node_type", sa.String(80), nullable=False),
        sa.Column("created_by", sa.String(120), nullable=False),
        _created(),
        sa.UniqueConstraint("curriculum_code", "grade", "subject_code", "stable_code", name="uq_curriculum_nodes_scope_stable_code"),
        sa.CheckConstraint("grade >= 0 AND grade <= 12", name="ck_curriculum_nodes_grade"),
        sa.CheckConstraint("node_type IN ('curriculum','phase','grade','subject','term','strand','topic','subtopic','skill','learning_objective','assessment_requirement','assessment_statement','prerequisite','vocabulary')", name="ck_curriculum_nodes_type"),
    )
    op.create_index("ix_curriculum_nodes_scope", "curriculum_nodes", ["curriculum_code", "grade", "subject_code"])

    op.create_table(
        "curriculum_node_versions",
        _uuid_pk("curriculum_node_version_id"),
        sa.Column("curriculum_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_nodes.curriculum_node_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("curriculum_code", sa.String(40), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("subject_code", sa.String(80), nullable=False),
        sa.Column("strand", sa.String(180), nullable=False),
        sa.Column("term", sa.String(40), nullable=True),
        sa.Column("topic", sa.String(240), nullable=False),
        sa.Column("subtopic", sa.String(240), nullable=True),
        sa.Column("skill", sa.String(240), nullable=True),
        sa.Column("learning_objective", sa.Text(), nullable=False),
        sa.Column("assessment_statement", sa.Text(), nullable=True),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("supersedes_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_node_versions.curriculum_node_version_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("created_by", sa.String(120), nullable=False),
        _created(),
        _jsonb("metadata_json"),
        sa.UniqueConstraint("curriculum_node_id", "created_at", name="uq_curriculum_node_versions_node_created"),
        sa.CheckConstraint("grade >= 0 AND grade <= 12", name="ck_curriculum_node_versions_grade"),
        sa.CheckConstraint("language IN ('en','af','nso','zu','xh')", name="ck_curriculum_node_versions_language"),
        sa.CheckConstraint("status IN ('draft','in_review','approved','superseded','withdrawn')", name="ck_curriculum_node_versions_status"),
        sa.CheckConstraint("effective_to IS NULL OR effective_from IS NULL OR effective_to >= effective_from", name="ck_curriculum_node_versions_effective_order"),
        sa.CheckConstraint("supersedes_version_id IS NULL OR supersedes_version_id <> curriculum_node_version_id", name="ck_curriculum_node_versions_no_self_supersession"),
    )
    op.create_index("ix_curriculum_node_versions_requirement", "curriculum_node_versions", ["curriculum_code", "grade", "subject_code", "status"])

    op.create_table(
        "curriculum_edge_versions",
        _uuid_pk("edge_version_id"),
        sa.Column("from_curriculum_node_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_node_versions.curriculum_node_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("to_curriculum_node_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_node_versions.curriculum_node_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("edge_type", sa.String(40), nullable=False),
        sa.Column("review_status", sa.String(32), nullable=False),
        sa.Column("proposed_by", sa.String(120), nullable=False),
        sa.Column("proposed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reviewed_by", sa.String(120), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("supersedes_edge_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_edge_versions.edge_version_id", ondelete="RESTRICT"), nullable=True),
        _jsonb("metadata_json"),
        sa.CheckConstraint("from_curriculum_node_version_id <> to_curriculum_node_version_id", name="ck_curriculum_edge_versions_distinct_nodes"),
        sa.CheckConstraint("edge_type IN ('prerequisite_of','sequence_before','supports','assesses','same_concept_as','translation_of')", name="ck_curriculum_edge_versions_type"),
        sa.CheckConstraint("review_status IN ('proposed','in_review','approved','rejected','needs_revision','superseded','withdrawn')", name="ck_curriculum_edge_versions_status"),
        sa.CheckConstraint("review_status <> 'approved' OR (reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)", name="ck_curriculum_edge_versions_approval_metadata"),
        sa.CheckConstraint("reviewed_by IS NULL OR reviewed_by <> proposed_by OR metadata_json ? 'maker_checker_exception_id'", name="ck_curriculum_edge_versions_maker_checker"),
        sa.CheckConstraint("supersedes_edge_version_id IS NULL OR supersedes_edge_version_id <> edge_version_id", name="ck_curriculum_edge_versions_no_self_supersession"),
    )
    op.create_index("ix_curriculum_edge_versions_from", "curriculum_edge_versions", ["from_curriculum_node_version_id", "edge_type"])
    op.create_index("ix_curriculum_edge_versions_to", "curriculum_edge_versions", ["to_curriculum_node_version_id", "edge_type"])

    op.create_table(
        "curriculum_source_mapping_versions",
        _uuid_pk("mapping_version_id"),
        sa.Column("mapping_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_chunk_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_chunk_versions.chunk_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("source_page_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_pages.page_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("source_section_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_sections.section_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("curriculum_node_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_node_versions.curriculum_node_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("support_type", sa.String(60), nullable=False),
        sa.Column("authority_tier", sa.String(16), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("language_status", sa.String(60), nullable=False),
        sa.Column("mapping_rationale", sa.Text(), nullable=False),
        sa.Column("proposed_by", sa.String(120), nullable=False),
        sa.Column("proposed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("review_status", sa.String(32), nullable=False),
        sa.Column("reviewed_by", sa.String(120), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("supersedes_mapping_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_mapping_versions.mapping_version_id", ondelete="RESTRICT"), nullable=True),
        _jsonb("metadata_json"),
        _created(),
        sa.UniqueConstraint("mapping_id", "mapping_version_id", name="uq_curriculum_source_mapping_versions_identity"),
        sa.CheckConstraint("support_type IN ('direct_support','example','assessment_evidence','teaching_guidance','background_context')", name="ck_curriculum_source_mapping_versions_support_type"),
        sa.CheckConstraint("authority_tier IN ('tier_1','tier_2','tier_3')", name="ck_curriculum_source_mapping_versions_tier"),
        sa.CheckConstraint("language IN ('en','af','nso','zu','xh')", name="ck_curriculum_source_mapping_versions_language"),
        sa.CheckConstraint("language_status IN ('official_source','approved_human_translation','machine_translation_draft','generated_learner_explanation')", name="ck_curriculum_source_mapping_versions_language_status"),
        sa.CheckConstraint("NOT (language_status = 'machine_translation_draft' AND authority_tier = 'tier_1')", name="ck_curriculum_source_mapping_versions_machine_not_tier1"),
        sa.CheckConstraint("review_status IN ('proposed','in_review','approved','rejected','needs_revision','superseded','withdrawn')", name="ck_curriculum_source_mapping_versions_review_status"),
        sa.CheckConstraint("review_status <> 'approved' OR (reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)", name="ck_curriculum_source_mapping_versions_approval_metadata"),
        sa.CheckConstraint("reviewed_by IS NULL OR reviewed_by <> proposed_by OR metadata_json ? 'maker_checker_exception_id'", name="ck_curriculum_source_mapping_versions_maker_checker"),
        sa.CheckConstraint("supersedes_mapping_version_id IS NULL OR supersedes_mapping_version_id <> mapping_version_id", name="ck_curriculum_source_mapping_versions_no_self_supersession"),
    )
    op.create_index("ix_curriculum_source_mapping_versions_node_status", "curriculum_source_mapping_versions", ["curriculum_node_version_id", "review_status"])
    op.create_index("ix_curriculum_source_mapping_versions_chunk", "curriculum_source_mapping_versions", ["source_chunk_version_id"])

    op.create_table(
        "curriculum_mapping_review_events",
        _uuid_pk("review_event_id"),
        sa.Column("mapping_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_mapping_versions.mapping_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("event_type", sa.String(60), nullable=False),
        sa.Column("actor_id", sa.String(120), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("previous_status", sa.String(32), nullable=True),
        sa.Column("next_status", sa.String(32), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("exception_id", sa.String(160), nullable=True),
        sa.Column("per_item_trace_id", sa.String(240), nullable=True),
        _jsonb("metadata_json"),
        sa.CheckConstraint("event_type IN ('proposed','moved_to_review','approved','rejected','needs_revision','withdrawn','superseded','single_developer_exception_recorded')", name="ck_curriculum_mapping_review_events_type"),
        sa.CheckConstraint("event_type <> 'approved' OR per_item_trace_id IS NOT NULL", name="ck_curriculum_mapping_review_events_approval_trace"),
    )
    op.create_index("ix_curriculum_mapping_review_events_mapping_time", "curriculum_mapping_review_events", ["mapping_version_id", "occurred_at"])

    op.create_table(
        "curriculum_language_links",
        _uuid_pk("language_link_id"),
        sa.Column("source_node_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_node_versions.curriculum_node_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("target_node_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_node_versions.curriculum_node_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("language_status", sa.String(60), nullable=False),
        sa.Column("review_status", sa.String(32), nullable=False),
        sa.Column("created_by", sa.String(120), nullable=False),
        _created(),
        sa.Column("reviewed_by", sa.String(120), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("source_node_version_id <> target_node_version_id", name="ck_curriculum_language_links_distinct_nodes"),
        sa.CheckConstraint("language_status IN ('official_source','approved_human_translation','machine_translation_draft','generated_learner_explanation')", name="ck_curriculum_language_links_status"),
        sa.CheckConstraint("review_status IN ('proposed','in_review','approved','rejected','needs_revision','superseded','withdrawn')", name="ck_curriculum_language_links_review_status"),
        sa.CheckConstraint("NOT (language_status = 'machine_translation_draft' AND review_status = 'approved')", name="ck_curriculum_language_links_machine_not_official"),
        sa.UniqueConstraint("source_node_version_id", "target_node_version_id", "language_status", name="uq_curriculum_language_links_pair_status"),
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION phase02r_prevent_approved_node_version_mutation()
        RETURNS trigger AS $$
        BEGIN
          IF OLD.status = 'approved' THEN
            RAISE EXCEPTION 'approved curriculum node versions are immutable; create a superseding version';
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_phase02r_prevent_approved_node_version_mutation
        BEFORE UPDATE ON curriculum_node_versions
        FOR EACH ROW EXECUTE FUNCTION phase02r_prevent_approved_node_version_mutation();
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION phase02r_prevent_mapping_review_event_mutation()
        RETURNS trigger AS $$
        BEGIN
          RAISE EXCEPTION 'mapping review events are append-only';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_phase02r_prevent_mapping_review_event_update
        BEFORE UPDATE ON curriculum_mapping_review_events
        FOR EACH ROW EXECUTE FUNCTION phase02r_prevent_mapping_review_event_mutation();
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_phase02r_prevent_mapping_review_event_delete
        BEFORE DELETE ON curriculum_mapping_review_events
        FOR EACH ROW EXECUTE FUNCTION phase02r_prevent_mapping_review_event_mutation();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_phase02r_prevent_mapping_review_event_delete ON curriculum_mapping_review_events")
    op.execute("DROP TRIGGER IF EXISTS trg_phase02r_prevent_mapping_review_event_update ON curriculum_mapping_review_events")
    op.execute("DROP FUNCTION IF EXISTS phase02r_prevent_mapping_review_event_mutation()")
    op.execute("DROP TRIGGER IF EXISTS trg_phase02r_prevent_approved_node_version_mutation ON curriculum_node_versions")
    op.execute("DROP FUNCTION IF EXISTS phase02r_prevent_approved_node_version_mutation()")
    op.drop_table("curriculum_language_links")
    op.drop_index("ix_curriculum_mapping_review_events_mapping_time", table_name="curriculum_mapping_review_events")
    op.drop_table("curriculum_mapping_review_events")
    op.drop_index("ix_curriculum_source_mapping_versions_chunk", table_name="curriculum_source_mapping_versions")
    op.drop_index("ix_curriculum_source_mapping_versions_node_status", table_name="curriculum_source_mapping_versions")
    op.drop_table("curriculum_source_mapping_versions")
    op.drop_index("ix_curriculum_edge_versions_to", table_name="curriculum_edge_versions")
    op.drop_index("ix_curriculum_edge_versions_from", table_name="curriculum_edge_versions")
    op.drop_table("curriculum_edge_versions")
    op.drop_index("ix_curriculum_node_versions_requirement", table_name="curriculum_node_versions")
    op.drop_table("curriculum_node_versions")
    op.drop_index("ix_curriculum_nodes_scope", table_name="curriculum_nodes")
    op.drop_table("curriculum_nodes")
