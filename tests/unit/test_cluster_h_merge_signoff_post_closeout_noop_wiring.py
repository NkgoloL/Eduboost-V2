from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_merge_signoff_post_closeout_noop_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_merge_signoff_post_closeout_noop_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make final-merge-signoff-lock-check" in text
    assert "make release-owner-post-closeout-decision-record-check" in text
    assert "make final-evidence-noop-execution-assertion-check" in text
    assert "tests/unit/test_cluster_h_merge_signoff_post_closeout_noop_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_merge_signoff_post_closeout_noop_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/final_merge_signoff_lock.md" in text
    assert "docs/operations/release_owner_post_closeout_decision_record.md" in text
    assert "docs/operations/final_evidence_noop_execution_assertion.md" in text


@pytest.mark.unit
def test_final_project_closeout_links_noop_execution_assertion() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_project_closeout_attestation.md").read_text(encoding="utf-8")
    assert "docs/operations/final_evidence_noop_execution_assertion.md" in text
