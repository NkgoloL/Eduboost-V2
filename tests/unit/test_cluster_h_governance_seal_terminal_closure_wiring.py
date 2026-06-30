from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_governance_seal_terminal_closure_wiring_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_governance_seal_terminal_closure_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make beta-governance-seal-check" in text
    assert "make beta-release-final-index-check" in text
    assert "make cluster-h-terminal-closure-assertion-check" in text
    assert "tests/unit/test_cluster_h_governance_seal_terminal_closure_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_terminal_closure_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")

    assert "docs/operations/beta_governance_seal_checklist.md" in text
    assert "docs/operations/beta_release_final_index.md" in text
    assert "docs/operations/cluster_h_terminal_closure_assertion.md" in text


@pytest.mark.unit
def test_project_release_closure_index_links_terminal_closure() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "project_release_closure_index.md").read_text(encoding="utf-8")

    assert "docs/operations/cluster_h_terminal_closure_assertion.md" in text
