from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_execution_pr_verification_wiring_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_execution_pr_verification_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make beta-release-execution-plan-check" in text
    assert "make beta-pr-body" in text
    assert "make beta-pr-body-check" in text
    assert "make final-release-verification-check" in text
    assert "tests/unit/test_cluster_h_execution_pr_verification_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_execution_pr_verification_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")

    assert "docs/operations/beta_release_execution_plan.md" in text
    assert "docs/operations/beta_release_pr_body.md" in text
    assert "docs/operations/final_release_verification_bundle.md" in text


@pytest.mark.unit
def test_pr_closeout_links_final_release_verification_bundle() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "pr_closeout_evidence_checklist.md").read_text(encoding="utf-8")

    assert "docs/operations/final_release_verification_bundle.md" in text
