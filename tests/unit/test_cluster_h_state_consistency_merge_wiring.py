from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_state_consistency_merge_wiring_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_state_consistency_merge_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make release-state-snapshot" in text
    assert "make release-state-snapshot-check" in text
    assert "make beta-evidence-consistency-check" in text
    assert "make final-pr-merge-readiness-check" in text
    assert "tests/unit/test_cluster_h_state_consistency_merge_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_state_consistency_merge_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")

    assert "docs/operations/release_state_snapshot.md" in text
    assert "docs/operations/beta_evidence_consistency_guard.md" in text
    assert "docs/operations/final_pr_merge_readiness_contract.md" in text


@pytest.mark.unit
def test_final_release_verification_links_merge_readiness() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_release_verification_bundle.md").read_text(encoding="utf-8")

    assert "docs/operations/final_pr_merge_readiness_contract.md" in text
