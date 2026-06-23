from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from app.services.curriculum.evaluation import (
    MIN_MRR,
    MIN_NEGATIVE_CASES,
    MIN_POSITIVE_CASES,
    MIN_PRECISION_AT_K,
    MIN_RECALL_AT_K,
    EvaluationRejectedError,
    Gate2R8EvaluationPolicy,
    RetrievalEvaluationCase,
    build_gate2r8_evaluation_cases,
    build_gate2r8_evaluation_report,
)
from app.services.curriculum.legacy_migration import (
    LegacyArtifactView,
    LegacyMigrationClassifier,
    build_gate2r8_legacy_migration_manifest,
)
from app.services.curriculum.phase02r_closure import (
    build_gate2r8_audit_bundle,
    collect_previous_gate_references,
    evaluate_closure_readiness,
)


def test_evaluation_dataset_has_required_positive_and_negative_cases() -> None:
    cases = build_gate2r8_evaluation_cases()
    assert sum(1 for case in cases if not case.is_negative_case) >= MIN_POSITIVE_CASES
    assert sum(1 for case in cases if case.is_negative_case) >= MIN_NEGATIVE_CASES


def test_evaluation_metrics_pass_gate_thresholds() -> None:
    result = Gate2R8EvaluationPolicy().evaluate(build_gate2r8_evaluation_cases())
    assert result.status == "passed"
    assert result.metrics.recall_at_k >= MIN_RECALL_AT_K
    assert result.metrics.precision_at_k >= MIN_PRECISION_AT_K
    assert result.metrics.mrr >= MIN_MRR


def test_negative_retrieval_case_with_authoritative_hit_is_rejected() -> None:
    bad_case = RetrievalEvaluationCase(
        case_id="bad-negative",
        language="en",
        strand="out_of_scope",
        term=None,
        query="unsupported topic",
        is_negative_case=True,
        retrieved_chunk_ids=("chunk-that-should-not-appear",),
    )
    with pytest.raises(EvaluationRejectedError):
        Gate2R8EvaluationPolicy().evaluate([bad_case] + list(build_gate2r8_evaluation_cases()))


def test_wrong_language_or_version_hits_are_rejected() -> None:
    case = replace(build_gate2r8_evaluation_cases()[0], wrong_language_hit_count=1)
    with pytest.raises(EvaluationRejectedError):
        Gate2R8EvaluationPolicy().evaluate([case] + list(build_gate2r8_evaluation_cases()[1:]))


def test_evaluation_report_is_deterministic_and_does_not_close_phase() -> None:
    first = build_gate2r8_evaluation_report()
    second = build_gate2r8_evaluation_report()
    assert first["status"] == "passed"
    assert first["report_sha256"] == second["report_sha256"]
    assert first["gate_boundary"]["phase_02r_completion_declared"] is False
    assert first["gate_boundary"]["production_activation_performed"] is False


def test_legacy_classifier_allows_only_grounded_verified_serving() -> None:
    classifier = LegacyMigrationClassifier()
    grounded = classifier.classify(
        LegacyArtifactView(
            artifact_id="grounded",
            artifact_type="assessment_item",
            published=True,
            source_snapshot_hash="snapshot",
            source_chunk_ids=("chunk",),
            answer_key_verified=True,
            generation_policy_version="phase02r-gate2r6-generation-v1",
        )
    )
    assert grounded.disposition == "grounded_verified"
    assert grounded.learner_serving_allowed is True

    ungrounded = classifier.classify(
        LegacyArtifactView(
            artifact_id="ungrounded",
            artifact_type="lesson",
            published=True,
            source_snapshot_hash=None,
        )
    )
    assert ungrounded.disposition == "quarantine_requires_review"
    assert ungrounded.learner_serving_allowed is False


def test_legacy_manifest_is_review_ready_and_non_executing() -> None:
    manifest = build_gate2r8_legacy_migration_manifest()
    assert manifest["status"] == "ready_for_review"
    assert manifest["gate_boundary"]["migration_executed"] is False
    assert manifest["gate_boundary"]["production_activation_performed"] is False
    assert manifest["learner_serving_allowed_count"] >= 1
    assert manifest["requires_human_review_count"] >= 1


def test_previous_gate_references_cover_2r4_to_2r7() -> None:
    refs = collect_previous_gate_references(Path.cwd())
    assert [ref.gate for ref in refs] == ["2R.4", "2R.5", "2R.6", "2R.7"]


def test_closure_readiness_is_candidate_only() -> None:
    readiness = evaluate_closure_readiness(Path.cwd())
    assert readiness.status == "ready_for_candidate_closure_evidence"
    assert readiness.evaluation_status == "passed"
    assert readiness.legacy_migration_status == "ready_for_review"


def test_audit_bundle_is_deterministic_and_non_closing() -> None:
    first = build_gate2r8_audit_bundle(Path.cwd())
    second = build_gate2r8_audit_bundle(Path.cwd())
    assert first["audit_bundle_sha256"] == second["audit_bundle_sha256"]
    assert first["gate_boundary"]["phase_02r_completion_declared"] is False
    assert first["gate_boundary"]["legacy_migration_executed"] is False


def test_gate2r8_required_paths_registered() -> None:
    from app.services.curriculum.phase02r_verification import validate_required_paths

    assert validate_required_paths("2R.8") == []
