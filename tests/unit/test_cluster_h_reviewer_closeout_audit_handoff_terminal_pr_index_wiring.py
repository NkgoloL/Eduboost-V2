from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_reviewer_closeout_audit_handoff_terminal_pr_index_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_reviewer_closeout_audit_handoff_terminal_pr_index_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make sealed-reviewer-closeout-packet-check" in text
    assert "make final-audit-handoff-register-check" in text
    assert "make terminal-pr-evidence-index-check" in text
    assert "tests/unit/test_cluster_h_reviewer_closeout_audit_handoff_terminal_pr_index_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_reviewer_closeout_audit_handoff_terminal_pr_index_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/sealed_reviewer_closeout_packet.md" in text
    assert "docs/operations/final_audit_handoff_register.md" in text
    assert "docs/operations/terminal_pr_evidence_index.md" in text


@pytest.mark.unit
def test_terminal_review_index_links_terminal_pr_evidence_index() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "terminal_review_index.md").read_text(encoding="utf-8")
    assert "docs/operations/terminal_pr_evidence_index.md" in text
