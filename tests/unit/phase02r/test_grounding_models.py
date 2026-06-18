from __future__ import annotations

from app.core.database import Base


def test_phase02r_grounding_model_tables_are_registered() -> None:
    required = {
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
        "curriculum_corpus_active_bindings",
        "curriculum_corpus_outbox_events",
        "curriculum_generation_grounding_records",
        "curriculum_claim_validation_records",
        "curriculum_answer_verification_records",
        "tutor_grounding_records",
        "curriculum_legacy_dispositions",
        "curriculum_retrieval_evaluation_runs",
        "curriculum_retrieval_evaluation_cases",
        "phase02r_audit_findings",
    }
    assert required <= set(Base.metadata.tables)


def test_active_binding_and_outbox_are_projection_tables() -> None:
    binding_columns = set(Base.metadata.tables["curriculum_corpus_active_bindings"].columns.keys())
    outbox_columns = set(Base.metadata.tables["curriculum_corpus_outbox_events"].columns.keys())
    assert {"activation_key", "corpus_version_id", "binding_epoch"} <= binding_columns
    assert {"processing_status", "attempts", "processed_at"} <= outbox_columns
