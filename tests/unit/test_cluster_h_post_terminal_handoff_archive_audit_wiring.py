from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_post_terminal_handoff_archive_audit_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_post_terminal_handoff_archive_audit_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make final-release-handoff-package-check" in text
    assert "make evidence-archive-completeness-guard-check" in text
    assert "make post-terminal-audit-readiness-check" in text
    assert "tests/unit/test_cluster_h_post_terminal_handoff_archive_audit_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_post_terminal_handoff_archive_audit_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/final_release_handoff_package.md" in text
    assert "docs/operations/evidence_archive_completeness_guard.md" in text
    assert "docs/operations/post_terminal_audit_readiness_assertion.md" in text


@pytest.mark.unit
def test_beta_release_final_index_links_post_terminal_audit_readiness() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "beta_release_final_index.md").read_text(encoding="utf-8")
    assert "docs/operations/post_terminal_audit_readiness_assertion.md" in text
