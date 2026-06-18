"""Phase 2R acquisition, extraction, corpus, grounding, tutor, and audit controls.

Revision ID: 20260618_1200_phase02r_grounding
Revises: 20260616_1200_phase02r_authority
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260618_1200_phase02r_grounding"
down_revision = "20260616_1200_phase02r_authority"
branch_labels = None
depends_on = None


def _uuid_pk(name: str) -> sa.Column:
    return sa.Column(name, postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))


def _j(name: str, default: str = "'{}'::jsonb") -> sa.Column:
    return sa.Column(name, postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text(default))


def _created() -> sa.Column:
    return sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())


def _sha_check(column: str, name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(f"{column} ~ '^[0-9a-f]{{64}}$'", name=name)


def _append_only(table: str) -> None:
    op.execute(
        f"""
        CREATE TRIGGER trg_{table}_append_only
        BEFORE UPDATE OR DELETE ON {table}
        FOR EACH ROW EXECUTE FUNCTION prevent_phase02r_grounding_mutation();
        """
    )


APPEND_ONLY_TABLES = (
    "curriculum_source_acquisition_runs",
    "curriculum_original_objects",
    "curriculum_extraction_runs",
    "curriculum_source_pages",
    "curriculum_source_sections",
    "curriculum_chunk_versions",
    "curriculum_graph_nodes",
    "curriculum_mapping_versions",
    "curriculum_corpus_versions",
    "curriculum_corpus_memberships",
    "curriculum_corpus_activation_events",
    "curriculum_generation_grounding_records",
    "curriculum_claim_validation_records",
    "curriculum_answer_verification_records",
    "tutor_grounding_records",
    "curriculum_legacy_dispositions",
    "curriculum_retrieval_evaluation_runs",
    "curriculum_retrieval_evaluation_cases",
    "phase02r_audit_findings",
)


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_phase02r_grounding_mutation()
        RETURNS trigger AS $$
        BEGIN
          RAISE EXCEPTION 'Phase 2R grounding records are append-only';
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.create_table(
        "curriculum_source_acquisition_runs",
        _uuid_pk("acquisition_run_id"),
        sa.Column("source_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("acquisition_method", sa.String(40), nullable=False),
        sa.Column("requested_uri", sa.String(1000), nullable=False),
        sa.Column("final_uri", sa.String(1000), nullable=True),
        sa.Column("operator_id", sa.String(120), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        _j("http_metadata"),
        _j("redirect_chain", "'[]'::jsonb"),
        sa.Column("malware_scan_status", sa.String(40), nullable=False, server_default="not_run"),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        _created(),
        sa.CheckConstraint("acquisition_method IN ('authorised_upload','approved_url','approved_api','checksum_refresh')", name="ck_curriculum_acquisition_method"),
        sa.CheckConstraint("status IN ('requested','acquired','quarantined','failed')", name="ck_curriculum_acquisition_status"),
    )
    op.create_index("ix_curriculum_acquisition_source_version", "curriculum_source_acquisition_runs", ["source_version_id", "created_at"])

    op.create_table(
        "curriculum_original_objects",
        _uuid_pk("original_object_id"),
        sa.Column("source_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("acquisition_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_acquisition_runs.acquisition_run_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("object_uri", sa.String(1000), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("media_type", sa.String(120), nullable=False),
        sa.Column("storage_backend", sa.String(80), nullable=False),
        sa.Column("encryption_state", sa.String(40), nullable=False, server_default="managed"),
        sa.Column("malware_scan_status", sa.String(40), nullable=False),
        sa.Column("acquired_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.String(120), nullable=False),
        _created(),
        sa.UniqueConstraint("source_version_id", "sha256", name="uq_curriculum_original_objects_source_hash"),
        _sha_check("sha256", "ck_curriculum_original_objects_sha256"),
        sa.CheckConstraint("size_bytes > 0", name="ck_curriculum_original_objects_size"),
    )

    op.create_table(
        "curriculum_extraction_runs",
        _uuid_pk("extraction_run_id"),
        sa.Column("source_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("original_object_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_original_objects.original_object_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("extractor_name", sa.String(120), nullable=False),
        sa.Column("extractor_version", sa.String(80), nullable=False),
        sa.Column("extraction_mode", sa.String(40), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=False, server_default="0"),
        _j("warnings", "'[]'::jsonb"),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("text_sha256", sa.String(64), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(120), nullable=False),
        _created(),
        sa.CheckConstraint("status IN ('requested','completed','review_required','rejected','failed')", name="ck_curriculum_extraction_runs_status"),
        sa.CheckConstraint("extraction_mode IN ('native_pdf','ocr','text_fixture','manual_review')", name="ck_curriculum_extraction_runs_mode"),
        sa.CheckConstraint("page_count >= 0", name="ck_curriculum_extraction_runs_page_count"),
        sa.CheckConstraint("quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)", name="ck_curriculum_extraction_runs_quality"),
        sa.CheckConstraint("text_sha256 IS NULL OR text_sha256 ~ '^[0-9a-f]{64}$'", name="ck_curriculum_extraction_runs_text_sha"),
    )

    op.create_table(
        "curriculum_source_pages",
        _uuid_pk("page_id"),
        sa.Column("extraction_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_extraction_runs.extraction_run_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("source_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("text_sha256", sa.String(64), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("extraction_confidence", sa.Float(), nullable=True),
        _j("coordinate_metadata"),
        _j("warnings", "'[]'::jsonb"),
        _created(),
        sa.UniqueConstraint("extraction_run_id", "page_number", name="uq_curriculum_source_pages_run_page"),
        sa.CheckConstraint("page_number > 0", name="ck_curriculum_source_pages_number"),
        _sha_check("text_sha256", "ck_curriculum_source_pages_sha"),
        sa.CheckConstraint("language IN ('en','af','nso')", name="ck_curriculum_source_pages_language"),
    )

    op.create_table(
        "curriculum_source_sections",
        _uuid_pk("section_id"),
        sa.Column("extraction_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_extraction_runs.extraction_run_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("source_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("parent_section_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_sections.section_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("section_order", sa.Integer(), nullable=False),
        sa.Column("heading", sa.String(500), nullable=True),
        sa.Column("page_start", sa.Integer(), nullable=False),
        sa.Column("page_end", sa.Integer(), nullable=False),
        sa.Column("text_sha256", sa.String(64), nullable=False),
        _j("metadata_json"),
        _created(),
        sa.UniqueConstraint("extraction_run_id", "section_order", name="uq_curriculum_sections_run_order"),
        sa.CheckConstraint("section_order >= 0", name="ck_curriculum_sections_order"),
        sa.CheckConstraint("page_start > 0 AND page_end >= page_start", name="ck_curriculum_sections_pages"),
        _sha_check("text_sha256", "ck_curriculum_sections_sha"),
    )

    op.create_table(
        "curriculum_chunk_versions",
        _uuid_pk("chunk_version_id"),
        sa.Column("source_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("extraction_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_extraction_runs.extraction_run_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("section_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_source_sections.section_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("chunk_order", sa.Integer(), nullable=False),
        sa.Column("page_start", sa.Integer(), nullable=False),
        sa.Column("page_end", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("text_sha256", sa.String(64), nullable=False),
        sa.Column("authority_tier", sa.String(16), nullable=False),
        sa.Column("rights_decision_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_rights_decisions.rights_decision_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("review_status", sa.String(32), nullable=False),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("embedding_model", sa.String(120), nullable=True),
        sa.Column("embedding_version", sa.String(80), nullable=True),
        sa.Column("embedding_sha256", sa.String(64), nullable=True),
        sa.Column("active_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active_to", sa.DateTime(timezone=True), nullable=True),
        _j("metadata_json"),
        _created(),
        sa.UniqueConstraint("extraction_run_id", "chunk_order", name="uq_curriculum_chunk_versions_run_order"),
        sa.CheckConstraint("page_start > 0 AND page_end >= page_start", name="ck_curriculum_chunk_versions_pages"),
        sa.CheckConstraint("language IN ('en','af','nso')", name="ck_curriculum_chunk_versions_language"),
        _sha_check("text_sha256", "ck_curriculum_chunk_versions_text_sha"),
        sa.CheckConstraint("authority_tier IN ('tier_1','tier_2','tier_3')", name="ck_curriculum_chunk_versions_authority_tier"),
        sa.CheckConstraint("review_status IN ('draft','review_required','approved','rejected','superseded')", name="ck_curriculum_chunk_versions_review_status"),
    )

    op.create_table(
        "curriculum_graph_nodes",
        _uuid_pk("node_id"),
        sa.Column("node_type", sa.String(80), nullable=False),
        sa.Column("code", sa.String(180), nullable=False),
        sa.Column("label", sa.String(500), nullable=False),
        sa.Column("curriculum", sa.String(80), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(120), nullable=True),
        sa.Column("language", sa.String(8), nullable=True),
        sa.Column("parent_node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_graph_nodes.node_id", ondelete="RESTRICT"), nullable=True),
        _j("metadata_json"),
        sa.Column("created_by", sa.String(120), nullable=False),
        _created(),
        sa.UniqueConstraint("curriculum", "grade", "subject", "language", "node_type", "code", name="uq_curriculum_graph_nodes_scope_code"),
    )

    op.create_table(
        "curriculum_mapping_versions",
        _uuid_pk("mapping_version_id"),
        sa.Column("chunk_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_chunk_versions.chunk_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_graph_nodes.node_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("relationship_type", sa.String(80), nullable=False),
        sa.Column("proposal_method", sa.String(80), nullable=False),
        sa.Column("review_status", sa.String(32), nullable=False),
        sa.Column("reviewed_by", sa.String(120), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("supersedes_mapping_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_mapping_versions.mapping_version_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("idempotency_key", sa.String(180), nullable=False),
        _created(),
        sa.CheckConstraint("review_status <> 'approved' OR (reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)", name="ck_curriculum_mapping_versions_approval_metadata"),
        sa.CheckConstraint("supersedes_mapping_version_id IS NULL OR supersedes_mapping_version_id <> mapping_version_id", name="ck_curriculum_mapping_versions_no_self_supersession"),
    )

    op.create_table(
        "curriculum_corpus_versions",
        _uuid_pk("corpus_version_id"),
        sa.Column("corpus_code", sa.String(180), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        _j("scope"),
        sa.Column("language", sa.String(8), nullable=False),
        _j("source_version_ids", "'[]'::jsonb"),
        _j("chunk_version_ids", "'[]'::jsonb"),
        _j("mapping_version_ids", "'[]'::jsonb"),
        sa.Column("embedding_model", sa.String(120), nullable=False),
        sa.Column("embedding_version", sa.String(80), nullable=False),
        sa.Column("manifest_sha256", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("review_status", sa.String(32), nullable=False),
        sa.Column("built_by", sa.String(120), nullable=False),
        sa.Column("built_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("supersedes_corpus_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=True),
        _created(),
        sa.UniqueConstraint("corpus_code", "version_number", name="uq_curriculum_corpus_versions_code_version"),
        _sha_check("manifest_sha256", "ck_curriculum_corpus_versions_manifest_sha"),
    )

    op.create_table(
        "curriculum_corpus_memberships",
        _uuid_pk("corpus_membership_id"),
        sa.Column("corpus_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("chunk_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_chunk_versions.chunk_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("mapping_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_mapping_versions.mapping_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("authority_tier", sa.String(16), nullable=False),
        sa.Column("retrieval_eligible", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("eligibility_reason", sa.Text(), nullable=True),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("corpus_version_id", "chunk_version_id", "mapping_version_id", name="uq_curriculum_corpus_memberships_unique"),
    )

    op.create_table(
        "curriculum_corpus_activation_events",
        _uuid_pk("activation_event_id"),
        sa.Column("corpus_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("activation_key", sa.String(240), nullable=False),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("previous_corpus_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("actor_id", sa.String(120), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("binding_epoch", sa.Integer(), nullable=False),
        _created(),
    )
    op.create_table(
        "curriculum_corpus_active_bindings",
        sa.Column("activation_key", sa.String(240), primary_key=True),
        sa.Column("corpus_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("activation_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_corpus_activation_events.activation_event_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("binding_epoch", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "curriculum_corpus_outbox_events",
        _uuid_pk("outbox_event_id"),
        sa.Column("activation_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_corpus_activation_events.activation_event_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        _j("payload"),
        sa.Column("processing_status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        _created(),
    )

    op.create_table(
        "curriculum_generation_grounding_records",
        _uuid_pk("grounding_record_id"),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("request_id", sa.String(160), nullable=False),
        sa.Column("corpus_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("policy_version", sa.String(80), nullable=False),
        sa.Column("retrieval_query", sa.Text(), nullable=False),
        _j("requested_objective_ids", "'[]'::jsonb"),
        _j("chunk_version_ids", "'[]'::jsonb"),
        _j("mapping_version_ids", "'[]'::jsonb"),
        _j("source_version_ids", "'[]'::jsonb"),
        _j("retrieval_scores", "'[]'::jsonb"),
        sa.Column("source_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("grounding_status", sa.String(32), nullable=False),
        _j("failure_reasons", "'[]'::jsonb"),
        sa.Column("provider", sa.String(80), nullable=True),
        sa.Column("model", sa.String(120), nullable=True),
        sa.Column("prompt_version", sa.String(80), nullable=True),
        _created(),
        sa.UniqueConstraint("request_id", name="uq_curriculum_generation_grounding_request"),
        _sha_check("source_snapshot_hash", "ck_curriculum_generation_grounding_snapshot"),
    )

    op.create_table(
        "curriculum_claim_validation_records",
        _uuid_pk("claim_validation_id"),
        sa.Column("grounding_record_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_generation_grounding_records.grounding_record_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("claim_type", sa.String(80), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        _j("supporting_chunk_version_ids", "'[]'::jsonb"),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("validator_version", sa.String(80), nullable=False),
        _j("evidence"),
        _created(),
    )
    op.create_table(
        "curriculum_answer_verification_records",
        _uuid_pk("answer_verification_id"),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("question_hash", sa.String(64), nullable=False),
        sa.Column("answer_hash", sa.String(64), nullable=False),
        sa.Column("reasoning_hash", sa.String(64), nullable=True),
        sa.Column("checker_type", sa.String(80), nullable=False),
        sa.Column("checker_version", sa.String(80), nullable=False),
        sa.Column("verification_status", sa.String(32), nullable=False),
        sa.Column("expected_answer", sa.Text(), nullable=True),
        sa.Column("observed_answer", sa.Text(), nullable=True),
        _j("evidence"),
        _created(),
        _sha_check("question_hash", "ck_curriculum_answer_verification_question_hash"),
        _sha_check("answer_hash", "ck_curriculum_answer_verification_answer_hash"),
    )
    op.create_table(
        "tutor_grounding_records",
        _uuid_pk("tutor_grounding_id"),
        sa.Column("session_id", sa.String(80), nullable=True),
        sa.Column("message_id", sa.String(80), nullable=True),
        sa.Column("learner_id", sa.String(80), nullable=True),
        sa.Column("corpus_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("retrieval_query", sa.Text(), nullable=False),
        _j("source_chunk_ids", "'[]'::jsonb"),
        _j("published_artifact_ids", "'[]'::jsonb"),
        _j("curriculum_node_ids", "'[]'::jsonb"),
        sa.Column("grounding_status", sa.String(32), nullable=False),
        sa.Column("fallback_reason", sa.Text(), nullable=True),
        sa.Column("source_snapshot_hash", sa.String(64), nullable=True),
        _j("safety_metadata"),
        _created(),
        sa.CheckConstraint("grounding_status = 'passed' OR fallback_reason IS NOT NULL", name="ck_tutor_grounding_records_fallback_reason"),
    )

    op.create_table(
        "curriculum_legacy_dispositions",
        _uuid_pk("legacy_disposition_id"),
        sa.Column("artifact_type", sa.String(80), nullable=False),
        sa.Column("artifact_id", sa.String(160), nullable=False),
        sa.Column("previous_publication_state", sa.String(80), nullable=True),
        sa.Column("disposition", sa.String(80), nullable=False),
        sa.Column("learner_serving_allowed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("rationale", sa.Text(), nullable=False),
        _j("evidence"),
        sa.Column("decided_by", sa.String(120), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("supersedes_disposition_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_legacy_dispositions.legacy_disposition_id", ondelete="RESTRICT"), nullable=True),
        _created(),
        sa.CheckConstraint("learner_serving_allowed IS FALSE OR disposition = 'grounded_verified'", name="ck_curriculum_legacy_dispositions_serving_allowed"),
    )
    op.create_table(
        "curriculum_retrieval_evaluation_runs",
        _uuid_pk("evaluation_run_id"),
        sa.Column("corpus_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("dataset_version", sa.String(120), nullable=False),
        _j("metrics"),
        sa.Column("prohibited_hit_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wrong_version_hit_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wrong_language_hit_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fallback_rate", sa.Float(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_by", sa.String(120), nullable=False),
        _created(),
    )
    op.create_table(
        "curriculum_retrieval_evaluation_cases",
        _uuid_pk("evaluation_case_id"),
        sa.Column("evaluation_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_retrieval_evaluation_runs.evaluation_run_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("case_id", sa.String(160), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("strand", sa.String(160), nullable=False),
        sa.Column("term", sa.Integer(), nullable=True),
        sa.Column("query", sa.Text(), nullable=False),
        _j("expected_chunk_version_ids", "'[]'::jsonb"),
        _j("retrieved_chunk_version_ids", "'[]'::jsonb"),
        sa.Column("is_negative_case", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(32), nullable=False),
        _j("metrics"),
        _created(),
        sa.UniqueConstraint("evaluation_run_id", "case_id", name="uq_curriculum_eval_cases_case"),
    )
    op.create_table(
        "phase02r_audit_findings",
        _uuid_pk("audit_finding_id"),
        sa.Column("gate", sa.String(16), nullable=False),
        sa.Column("finding_code", sa.String(120), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("finding", sa.Text(), nullable=False),
        sa.Column("corrective_action", sa.Text(), nullable=True),
        _j("evidence"),
        sa.Column("auditor_id", sa.String(120), nullable=False),
        _created(),
    )

    for table in APPEND_ONLY_TABLES:
        _append_only(table)


def downgrade() -> None:
    for table in reversed(APPEND_ONLY_TABLES):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_append_only ON {table}")
    for table in (
        "phase02r_audit_findings",
        "curriculum_retrieval_evaluation_cases",
        "curriculum_retrieval_evaluation_runs",
        "curriculum_legacy_dispositions",
        "tutor_grounding_records",
        "curriculum_answer_verification_records",
        "curriculum_claim_validation_records",
        "curriculum_generation_grounding_records",
        "curriculum_corpus_outbox_events",
        "curriculum_corpus_active_bindings",
        "curriculum_corpus_activation_events",
        "curriculum_corpus_memberships",
        "curriculum_corpus_versions",
        "curriculum_mapping_versions",
        "curriculum_graph_nodes",
        "curriculum_chunk_versions",
        "curriculum_source_sections",
        "curriculum_source_pages",
        "curriculum_extraction_runs",
        "curriculum_original_objects",
        "curriculum_source_acquisition_runs",
    ):
        op.drop_table(table)
    op.execute("DROP FUNCTION IF EXISTS prevent_phase02r_grounding_mutation()")
