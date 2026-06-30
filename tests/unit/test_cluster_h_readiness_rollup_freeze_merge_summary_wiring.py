from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_readiness_rollup_freeze_merge_summary_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_readiness_rollup_freeze_merge_summary_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make final-release-readiness-rollup-check" in text
    assert "make evidence-freeze-confirmation-record-check" in text
    assert "make pr-merge-evidence-summary-check" in text
    assert "tests/unit/test_cluster_h_readiness_rollup_freeze_merge_summary_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_readiness_rollup_freeze_merge_summary_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/final_release_readiness_rollup.md" in text
    assert "docs/operations/evidence_freeze_confirmation_record.md" in text
    assert "docs/operations/pr_merge_evidence_summary.md" in text


@pytest.mark.unit
def test_merge_control_gate_links_pr_merge_summary() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "merge_control_evidence_gate.md").read_text(encoding="utf-8")
    assert "docs/operations/pr_merge_evidence_summary.md" in text
