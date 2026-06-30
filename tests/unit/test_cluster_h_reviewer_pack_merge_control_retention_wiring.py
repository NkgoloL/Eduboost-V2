from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_reviewer_pack_merge_control_retention_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_reviewer_pack_merge_control_retention_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make final-reviewer-pack-checklist-check" in text
    assert "make merge-control-evidence-gate-check" in text
    assert "make release-evidence-retention-finalization-check" in text
    assert "tests/unit/test_cluster_h_reviewer_pack_merge_control_retention_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_reviewer_pack_merge_control_retention_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/final_reviewer_pack_checklist.md" in text
    assert "docs/operations/merge_control_evidence_gate.md" in text
    assert "docs/operations/release_evidence_retention_finalization.md" in text


@pytest.mark.unit
def test_pr_ready_certificate_links_merge_control_gate() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "pr_ready_final_closure_certificate.md").read_text(encoding="utf-8")
    assert "docs/operations/merge_control_evidence_gate.md" in text
