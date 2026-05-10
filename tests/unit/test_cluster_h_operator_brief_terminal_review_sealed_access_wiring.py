from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_operator_brief_terminal_review_sealed_access_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_operator_brief_terminal_review_sealed_access_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make final-release-operator-brief-check" in text
    assert "make terminal-review-index-check" in text
    assert "make sealed-evidence-access-handoff-check" in text
    assert "tests/unit/test_cluster_h_operator_brief_terminal_review_sealed_access_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_operator_brief_terminal_review_sealed_access_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/final_release_operator_brief.md" in text
    assert "docs/operations/terminal_review_index.md" in text
    assert "docs/operations/sealed_evidence_access_handoff.md" in text


@pytest.mark.unit
def test_terminal_evidence_seal_links_terminal_review_index() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "terminal_evidence_seal.md").read_text(encoding="utf-8")
    assert "docs/operations/terminal_review_index.md" in text
