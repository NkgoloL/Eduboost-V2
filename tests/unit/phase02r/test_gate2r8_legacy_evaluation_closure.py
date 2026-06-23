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


def test_previous_gate_references_cover_full_chain_2r0_to_2r7() -> None:
    refs = collect_previous_gate_references(Path.cwd())
    assert [ref.gate for ref in refs] == ["2R.0", "2R.1", "2R.2", "2R.3", "2R.4", "2R.5", "2R.6", "2R.7"]


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


# ---------------------------------------------------------------------------
# Regression tests for terminal Phase 02R closure support
# ---------------------------------------------------------------------------

def test_gate_control_validates_current_2r7_to_2r8_state() -> None:
    """Existing gate state (approved=2R.7, authorised=2R.8) must still validate cleanly when mocked."""
    import json
    import tempfile
    from pathlib import Path
    from unittest.mock import patch, MagicMock
    import scripts.phase02r_gate_control as gc

    # Since the workspace might be in terminal state, we mock a valid 2R.7->2R.8 control file
    control_content = {
        "phase": "02R",
        "start_approved": True,
        "approval_decision_commit_sha": "a" * 40,
        "evidence_commit_sha": "b" * 40,
        "approved_gate": "2R.7",
        "authorised_next_gate": "2R.8",
        "approved_at": "2026-06-23T22:00:00+02:00",
        "transition_commit_sha": "c" * 40,
        "remote_branch_sha_at_transition": "c" * 40,
    }

    minimal_approvals = {
        "gate": "2R.7",
        "authorised_next_gate": "2R.8",
        "decision": "approved_with_disclosed_self_review_exception",
        "evidence_source_sha": "d" * 40,
        "evidence_commit_sha": "b" * 40,
        "decisions": [],
        "decided_at": "2026-06-23T22:00:00+02:00",
    }

    def load_side_effect(p):
        path_str = str(p)
        if path_str.endswith("control.json"):
            return control_content
        elif "phase_02r_gate_automation.json" in path_str:
            return {
                "supported_gates": {
                    "2R.8": {"apply": True, "collect": True, "preflight": True, "verify": True}
                }
            }
        else:
            return minimal_approvals

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "control.json").write_text(json.dumps(control_content), encoding="utf-8")
        with (
            patch.object(gc, "CONTROL_PATH", tmp / "control.json"),
            patch.object(gc, "_evidence_index_metadata", return_value=(None, "d" * 40, "candidate")),
            patch.object(gc, "_validate_raw_checksums", return_value=None),
            patch.object(gc, "_load", side_effect=load_side_effect),
            patch.object(gc, "_approvals_path", return_value=MagicMock()),
            patch.object(gc, "_evidence_index_path", return_value=MagicMock(exists=lambda: False)),
            patch.object(gc, "_evidence_raw_dir", return_value=MagicMock()),
            patch.object(gc, "_validate_plan_current_state", return_value=None),
        ):
            errors = gc.validate_state(
                expected_approved_gate="2R.7",
                expected_authorised_gate="2R.8",
            )
    assert errors == [], f"Unexpected errors: {errors}"


def test_gate_control_rejects_nonexistent_gate_2r9() -> None:
    """Gate 2R.8 must not be able to authorise a nonexistent Gate 2R.9."""
    from scripts.phase02r_gate_control import GATE_ORDER

    assert "2R.9" not in GATE_ORDER, "Gate 2R.9 must not exist in GATE_ORDER"


def test_terminal_closure_requires_null_authorised_gate_and_phase_status() -> None:
    """validate_state must reject a terminal-shaped control lacking required terminal fields."""
    import json
    import tempfile
    from pathlib import Path
    from unittest.mock import patch

    import scripts.phase02r_gate_control as gc

    # Build a minimal control that looks terminal but is missing terminal fields.
    terminal_control_bad = {
        "phase": "02R",
        "start_approved": True,
        "approved_gate": "2R.8",
        "authorised_next_gate": None,
        # Missing phase_status, final_closure_commit_sha, final_audit_bundle_sha256
        "approval_decision_commit_sha": "a" * 40,
        "evidence_commit_sha": "b" * 40,
        "approved_at": "2026-06-23T22:00:00+02:00",
    }
    terminal_control_good = {
        **terminal_control_bad,
        "phase_status": "closed",
        "final_closure_commit_sha": "c" * 40,
        "final_audit_bundle_sha256": "d" * 64,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "control.json").write_text(json.dumps(terminal_control_bad), encoding="utf-8")
        with patch.object(gc, "CONTROL_PATH", tmp / "control.json"):
            errors = gc.validate_state()
        assert any("phase_status" in e or "final_closure_commit_sha" in e or "final_audit_bundle_sha256" in e for e in errors), \
            f"Expected terminal-field errors, got: {errors}"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "control.json").write_text(json.dumps(terminal_control_good), encoding="utf-8")
        with patch.object(gc, "CONTROL_PATH", tmp / "control.json"):
            errors_good = gc.validate_state()
        # Should fail on approvals/evidence (files don't exist), but NOT on terminal field checks.
        terminal_field_errors = [e for e in errors_good if any(
            kw in e for kw in ("phase_status", "final_closure_commit_sha", "final_audit_bundle_sha256")
        )]
        assert terminal_field_errors == [], f"Terminal fields should be valid, but got: {terminal_field_errors}"


def test_closure_requires_all_prior_gate_evidence_files_present() -> None:
    """evaluate_closure_readiness must report missing evidence for any gate in the full chain."""
    import tempfile
    from pathlib import Path

    from app.services.curriculum.phase02r_closure import REQUIRED_PREVIOUS_GATES, evaluate_closure_readiness

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Create a dummy root with no evidence files.
        readiness = evaluate_closure_readiness(root)
        assert readiness.status == "blocked"
        missing = [r for r in readiness.evidence_references if r.evidence_index_sha256 is None]
        assert len(missing) == len(REQUIRED_PREVIOUS_GATES), (
            f"Expected all {len(REQUIRED_PREVIOUS_GATES)} gates to be reported missing, got {len(missing)}"
        )


def test_final_closure_commit_must_differ_from_evidence_and_approval_commits() -> None:
    """_validate_gate_approval must reject terminal state where final_closure_commit_sha == evidence commit."""
    import scripts.phase02r_gate_control as gc
    from unittest.mock import MagicMock, patch

    shared_sha = "a" * 40  # deliberately reused to trigger the separation checks

    control = {
        "phase": "02R",
        "start_approved": True,
        "approved_gate": "2R.8",
        "authorised_next_gate": None,
        "phase_status": "closed",
        "approval_decision_commit_sha": "b" * 40,
        "evidence_commit_sha": shared_sha,
        "final_closure_commit_sha": shared_sha,  # same as evidence — must be rejected
        "final_audit_bundle_sha256": "e" * 64,
        "approved_at": "2026-06-23T22:00:00+02:00",
    }

    errors: list[str] = []

    # Provide a minimal approvals stub that passes the gate/phase_status checks but
    # does NOT override final_closure_commit_sha so the SHA comparison is reached.
    minimal_approvals = {
        "gate": "2R.8",
        "authorised_next_gate": None,
        "phase_status": "closed",
        "evidence_source_sha": shared_sha,
        "evidence_commit_sha": shared_sha,
        "decisions": [],
    }

    with (
        patch.object(gc, "_evidence_index_metadata", return_value=(None, shared_sha, "candidate")),
        patch.object(gc, "_validate_raw_checksums", return_value=None),
        patch.object(gc, "_load", return_value=minimal_approvals),
        patch.object(gc, "_approvals_path", return_value=MagicMock()),
        patch.object(gc, "_evidence_index_path", return_value=MagicMock(exists=lambda: False)),
        patch.object(gc, "_evidence_raw_dir", return_value=MagicMock()),
    ):
        gc._validate_gate_approval(
            approved_gate="2R.8",
            authorised_gate=None,
            control=control,
            require_approval_roles=False,
            require_evidence_index_sha=False,
            errors=errors,
        )

    assert any("final closure commit" in e and "separate" in e for e in errors), (
        f"Expected final closure commit separation error, got: {errors}"
    )
