"""Phase 2R source authority, rights, inventory, and review ledgers.

Revision ID: 20260616_1200_phase02r_authority
Revises: 20260615_2100_p17_reconcile
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260616_1200_phase02r_authority"
down_revision = "20260615_2100_p17_reconcile"
branch_labels = None
depends_on = None


def _uuid_pk(name: str) -> sa.Column:
    return sa.Column(
        name,
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )


def _create_append_only_trigger(table_name: str) -> None:
    trigger_name = f"trg_{table_name}_append_only"
    op.execute(
        f"""
        CREATE TRIGGER {trigger_name}
        BEFORE UPDATE OR DELETE ON {table_name}
        FOR EACH ROW EXECUTE FUNCTION prevent_phase02r_authority_mutation();
        """
    )


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_phase02r_authority_mutation()
        RETURNS trigger AS $$
        BEGIN
          RAISE EXCEPTION 'Phase 2R authority records are append-only';
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.create_table(
        "curriculum_sources",
        _uuid_pk("source_id"),
        sa.Column("publisher", sa.String(length=200), nullable=False),
        sa.Column("authority_tier", sa.String(length=16), nullable=False),
        sa.Column("official_source_url", sa.String(length=1000), nullable=True),
        sa.Column("document_title", sa.String(length=500), nullable=False),
        sa.Column("document_type", sa.String(length=80), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False, server_default="ZA"),
        sa.Column("curriculum", sa.String(length=80), nullable=False, server_default="CAPS"),
        sa.Column("phase", sa.String(length=80), nullable=True),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(length=120), nullable=True),
        sa.Column("language", sa.String(length=8), nullable=False),
        sa.Column("created_by", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("authority_tier IN ('tier_1','tier_2','tier_3')", name="ck_curriculum_sources_authority_tier"),
        sa.CheckConstraint("grade IS NULL OR (grade >= 0 AND grade <= 12)", name="ck_curriculum_sources_grade"),
        sa.CheckConstraint("language IN ('en','af','nso')", name="ck_curriculum_sources_language"),
    )
    op.create_index(
        "ix_curriculum_sources_scope",
        "curriculum_sources",
        ["curriculum", "grade", "subject", "language", "authority_tier"],
    )

    op.create_table(
        "curriculum_source_versions",
        _uuid_pk("source_version_id"),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("curriculum_sources.source_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("version_label", sa.String(length=160), nullable=False),
        sa.Column("publication_date", sa.Date(), nullable=True),
        sa.Column("effective_from", sa.Date(), nullable=True),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column(
            "supersedes_source_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("copyright_owner", sa.String(length=300), nullable=True),
        sa.Column("original_sha256", sa.String(length=64), nullable=False),
        sa.Column("original_object_uri", sa.String(length=1000), nullable=False),
        sa.Column("media_type", sa.String(length=120), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "retrieval_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_by", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source_id", "version_label", name="uq_curriculum_source_versions_source_label"),
        sa.UniqueConstraint("source_id", "original_sha256", name="uq_curriculum_source_versions_source_hash"),
        sa.CheckConstraint("original_sha256 ~ '^[0-9a-f]{64}$'", name="ck_curriculum_source_versions_sha256"),
        sa.CheckConstraint("file_size_bytes > 0", name="ck_curriculum_source_versions_file_size"),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_from IS NULL OR effective_to >= effective_from",
            name="ck_curriculum_source_versions_effective_dates",
        ),
        sa.CheckConstraint(
            "supersedes_source_version_id IS NULL OR supersedes_source_version_id <> source_version_id",
            name="ck_curriculum_source_versions_no_self_supersession",
        ),
    )
    op.create_index(
        "ix_curriculum_source_versions_source_effective",
        "curriculum_source_versions",
        ["source_id", "effective_from", "effective_to"],
    )

    op.create_table(
        "curriculum_rights_decisions",
        _uuid_pk("rights_decision_id"),
        sa.Column(
            "source_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("decision_status", sa.String(length=40), nullable=False),
        *[
            sa.Column(column, sa.Boolean(), nullable=False, server_default=sa.false())
            for column in (
                "may_store_original",
                "may_extract",
                "may_embed",
                "may_use_for_retrieval",
                "may_include_in_model_prompt",
                "may_generate_derivatives",
                "may_translate",
                "may_publish_translation",
                "may_show_excerpt_to_educator",
                "may_show_excerpt_to_learner",
                "may_redistribute",
                "may_use_commercially",
                "may_use_for_model_training",
                "requires_attribution",
            )
        ],
        sa.Column(
            "conditions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("decision_basis", sa.Text(), nullable=False),
        sa.Column("evidence_uri", sa.String(length=1000), nullable=False),
        sa.Column("reviewed_by", sa.String(length=120), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "supersedes_decision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("curriculum_rights_decisions.rights_decision_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("idempotency_key", sa.String(length=180), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "decision_status IN ('pending','approved','approved_with_conditions','denied','expired','withdrawn','disputed')",
            name="ck_curriculum_rights_decisions_status",
        ),
        sa.CheckConstraint(
            "supersedes_decision_id IS NULL OR supersedes_decision_id <> rights_decision_id",
            name="ck_curriculum_rights_decisions_no_self_supersession",
        ),
        sa.CheckConstraint(
            "decision_status <> 'approved_with_conditions' OR conditions <> '{}'::jsonb",
            name="ck_curriculum_rights_decisions_conditions_required",
        ),
        sa.UniqueConstraint("reviewed_by", "idempotency_key", name="uq_curriculum_rights_decisions_actor_idempotency"),
    )
    op.create_index(
        "ix_curriculum_rights_decisions_version_reviewed",
        "curriculum_rights_decisions",
        ["source_version_id", "reviewed_at"],
    )

    op.create_table(
        "curriculum_inventory_versions",
        _uuid_pk("inventory_version_id"),
        sa.Column("inventory_code", sa.String(length=160), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("curriculum", sa.String(length=80), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(length=120), nullable=False),
        sa.Column("delivery_languages", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("terms", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("strands", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("manifest_sha256", sa.String(length=64), nullable=False),
        sa.Column(
            "supersedes_inventory_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("curriculum_inventory_versions.inventory_version_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("frozen_by", sa.String(length=120), nullable=True),
        sa.Column("frozen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("inventory_code", "version_number", name="uq_curriculum_inventory_versions_code_version"),
        sa.CheckConstraint("version_number > 0", name="ck_curriculum_inventory_versions_version_positive"),
        sa.CheckConstraint("grade >= 0 AND grade <= 12", name="ck_curriculum_inventory_versions_grade"),
        sa.CheckConstraint("status IN ('draft','frozen','superseded')", name="ck_curriculum_inventory_versions_status"),
        sa.CheckConstraint("manifest_sha256 ~ '^[0-9a-f]{64}$'", name="ck_curriculum_inventory_versions_sha256"),
        sa.CheckConstraint(
            "status <> 'frozen' OR (frozen_by IS NOT NULL AND frozen_at IS NOT NULL)",
            name="ck_curriculum_inventory_versions_frozen_metadata",
        ),
        sa.CheckConstraint(
            "supersedes_inventory_version_id IS NULL OR supersedes_inventory_version_id <> inventory_version_id",
            name="ck_curriculum_inventory_versions_no_self_supersession",
        ),
    )

    op.create_table(
        "curriculum_inventory_items",
        _uuid_pk("inventory_item_id"),
        sa.Column(
            "inventory_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("curriculum_inventory_versions.inventory_version_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("requirement_code", sa.String(length=180), nullable=False),
        sa.Column("requirement_type", sa.String(length=80), nullable=False),
        sa.Column("authority_tier", sa.String(length=16), nullable=False),
        sa.Column("term", sa.Integer(), nullable=True),
        sa.Column("strand", sa.String(length=160), nullable=True),
        sa.Column("language", sa.String(length=8), nullable=True),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("curriculum_sources.source_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "source_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("item_status", sa.String(length=32), nullable=False),
        sa.Column("absence_reason", sa.Text(), nullable=True),
        sa.Column(
            "evidence",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("reviewed_by", sa.String(length=120), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("inventory_version_id", "requirement_code", name="uq_curriculum_inventory_items_requirement"),
        sa.CheckConstraint("authority_tier IN ('tier_1','tier_2','tier_3')", name="ck_curriculum_inventory_items_authority_tier"),
        sa.CheckConstraint("term IS NULL OR term BETWEEN 1 AND 4", name="ck_curriculum_inventory_items_term"),
        sa.CheckConstraint("language IS NULL OR language IN ('en','af','nso')", name="ck_curriculum_inventory_items_language"),
        sa.CheckConstraint(
            "item_status IN ('pending','located','absence_approved','rejected')",
            name="ck_curriculum_inventory_items_status",
        ),
        sa.CheckConstraint(
            "item_status <> 'located' OR (source_id IS NOT NULL AND source_version_id IS NOT NULL)",
            name="ck_curriculum_inventory_items_located_source_version",
        ),
        sa.CheckConstraint(
            "item_status <> 'absence_approved' OR (absence_reason IS NOT NULL AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)",
            name="ck_curriculum_inventory_items_absence_review",
        ),
    )
    op.create_index(
        "ix_curriculum_inventory_items_scope",
        "curriculum_inventory_items",
        ["inventory_version_id", "term", "strand", "language"],
    )

    op.create_table(
        "curriculum_review_decisions",
        _uuid_pk("review_decision_id"),
        sa.Column("review_domain", sa.String(length=40), nullable=False),
        sa.Column("subject_type", sa.String(length=80), nullable=False),
        sa.Column("subject_id", sa.String(length=120), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("reviewer_id", sa.String(length=120), nullable=False),
        sa.Column("reviewer_role", sa.String(length=120), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column(
            "evidence",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "supersedes_review_decision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("curriculum_review_decisions.review_decision_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("idempotency_key", sa.String(length=180), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "review_domain IN ('source_authority','rights','inventory_completeness','extraction','curriculum_mapping','generated_content','answer_verification')",
            name="ck_curriculum_review_decisions_domain",
        ),
        sa.CheckConstraint("decision IN ('approve','reject','request_changes')", name="ck_curriculum_review_decisions_decision"),
        sa.CheckConstraint(
            "supersedes_review_decision_id IS NULL OR supersedes_review_decision_id <> review_decision_id",
            name="ck_curriculum_review_decisions_no_self_supersession",
        ),
        sa.UniqueConstraint("reviewer_id", "idempotency_key", name="uq_curriculum_review_decisions_actor_idempotency"),
    )
    op.create_index(
        "ix_curriculum_review_decisions_subject",
        "curriculum_review_decisions",
        ["review_domain", "subject_type", "subject_id", "created_at"],
    )

    for table_name in (
        "curriculum_sources",
        "curriculum_source_versions",
        "curriculum_rights_decisions",
        "curriculum_inventory_versions",
        "curriculum_inventory_items",
        "curriculum_review_decisions",
    ):
        _create_append_only_trigger(table_name)


def downgrade() -> None:
    for table_name in reversed(
        (
            "curriculum_sources",
            "curriculum_source_versions",
            "curriculum_rights_decisions",
            "curriculum_inventory_versions",
            "curriculum_inventory_items",
            "curriculum_review_decisions",
        )
    ):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table_name}_append_only ON {table_name}")

    op.drop_index("ix_curriculum_review_decisions_subject", table_name="curriculum_review_decisions")
    op.drop_table("curriculum_review_decisions")
    op.drop_index("ix_curriculum_inventory_items_scope", table_name="curriculum_inventory_items")
    op.drop_table("curriculum_inventory_items")
    op.drop_table("curriculum_inventory_versions")
    op.drop_index("ix_curriculum_rights_decisions_version_reviewed", table_name="curriculum_rights_decisions")
    op.drop_table("curriculum_rights_decisions")
    op.drop_index("ix_curriculum_source_versions_source_effective", table_name="curriculum_source_versions")
    op.drop_table("curriculum_source_versions")
    op.drop_index("ix_curriculum_sources_scope", table_name="curriculum_sources")
    op.drop_table("curriculum_sources")
    op.execute("DROP FUNCTION IF EXISTS prevent_phase02r_authority_mutation")
