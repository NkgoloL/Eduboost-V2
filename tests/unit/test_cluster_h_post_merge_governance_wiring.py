from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_post_merge_governance_wiring_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_post_merge_governance_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make post-merge-release-handoff-check" in text
    assert "make release-owner-accountability-check" in text
    assert "make beta-release-decision-log-check" in text
    assert "tests/unit/test_cluster_h_post_merge_governance_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_post_merge_governance_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")

    assert "docs/operations/post_merge_release_handoff_checklist.md" in text
    assert "docs/operations/release_owner_accountability_matrix.md" in text
    assert "docs/operations/beta_release_decision_log.md" in text


@pytest.mark.unit
def test_final_pr_merge_readiness_links_post_merge_handoff() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_pr_merge_readiness_contract.md").read_text(encoding="utf-8")

    assert "docs/operations/post_merge_release_handoff_checklist.md" in text
    assert "docs/operations/release_owner_accountability_matrix.md" in text
    assert "docs/operations/beta_release_decision_log.md" in text
