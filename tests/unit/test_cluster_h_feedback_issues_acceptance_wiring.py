from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_feedback_issues_acceptance_wiring_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_feedback_issues_acceptance_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make beta-feedback-intake-contract-check" in text
    assert "make beta-known-issues-register-check" in text
    assert "make beta-acceptance-exit-criteria-check" in text
    assert "tests/unit/test_cluster_h_feedback_issues_acceptance_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_feedback_issues_acceptance_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")

    assert "docs/operations/beta_feedback_intake_contract.md" in text
    assert "docs/operations/beta_known_issues_register.md" in text
    assert "docs/operations/beta_acceptance_exit_criteria.md" in text


@pytest.mark.unit
def test_beta_release_decision_log_links_exit_criteria() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "beta_release_decision_log.md").read_text(encoding="utf-8")

    assert "docs/operations/beta_acceptance_exit_criteria.md" in text
