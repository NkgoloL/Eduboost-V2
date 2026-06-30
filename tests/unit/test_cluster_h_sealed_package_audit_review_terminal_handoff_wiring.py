from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_sealed_package_audit_review_terminal_handoff_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_sealed_package_audit_review_terminal_handoff_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make final-sealed-package-manifest-check" in text
    assert "make audit-review-closeout-certificate-check" in text
    assert "make terminal-handoff-closure-note-check" in text
    assert "tests/unit/test_cluster_h_sealed_package_audit_review_terminal_handoff_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_sealed_package_audit_review_terminal_handoff_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/final_sealed_package_manifest.md" in text
    assert "docs/operations/audit_review_closeout_certificate.md" in text
    assert "docs/operations/terminal_handoff_closure_note.md" in text


@pytest.mark.unit
def test_terminal_pr_index_links_final_sealed_package_manifest() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "terminal_pr_evidence_index.md").read_text(encoding="utf-8")
    assert "docs/operations/final_sealed_package_manifest.md" in text
