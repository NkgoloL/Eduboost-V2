from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_closure_manifest_branch_handoff_reviewer_decision_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_closure_manifest_branch_handoff_reviewer_decision_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make final-closure-manifest-check" in text
    assert "make branch-handoff-proof-record-check" in text
    assert "make reviewer-decision-capture-template-check" in text
    assert "tests/unit/test_cluster_h_closure_manifest_branch_handoff_reviewer_decision_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_closure_manifest_branch_handoff_reviewer_decision_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/final_closure_manifest.md" in text
    assert "docs/operations/branch_handoff_proof_record.md" in text
    assert "docs/operations/reviewer_decision_capture_template.md" in text


@pytest.mark.unit
def test_final_acceptance_memo_links_final_closure_manifest() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_acceptance_memo.md").read_text(encoding="utf-8")
    assert "docs/operations/final_closure_manifest.md" in text
