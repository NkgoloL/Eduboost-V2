from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_reviewer_disposition_terminal_seal_pr_handoff_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_reviewer_disposition_terminal_seal_pr_handoff_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make final-reviewer-disposition-record-check" in text
    assert "make terminal-evidence-seal-check" in text
    assert "make final-pr-handoff-summary-check" in text
    assert "tests/unit/test_cluster_h_reviewer_disposition_terminal_seal_pr_handoff_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_reviewer_disposition_terminal_seal_pr_handoff_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/final_reviewer_disposition_record.md" in text
    assert "docs/operations/terminal_evidence_seal.md" in text
    assert "docs/operations/final_pr_handoff_summary.md" in text


@pytest.mark.unit
def test_final_closure_manifest_links_terminal_evidence_seal() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_closure_manifest.md").read_text(encoding="utf-8")
    assert "docs/operations/terminal_evidence_seal.md" in text
