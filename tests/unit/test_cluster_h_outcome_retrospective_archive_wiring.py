from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_outcome_retrospective_archive_wiring_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_outcome_retrospective_archive_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make beta-outcome-report-template-check" in text
    assert "make beta-retrospective-action-register-check" in text
    assert "make post-beta-evidence-archive-manifest-check" in text
    assert "tests/unit/test_cluster_h_outcome_retrospective_archive_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_outcome_retrospective_archive_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")

    assert "docs/operations/beta_outcome_report_template.md" in text
    assert "docs/operations/beta_retrospective_action_register.md" in text
    assert "docs/operations/post_beta_evidence_archive_manifest.md" in text


@pytest.mark.unit
def test_beta_acceptance_exit_criteria_links_outcome_archive() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "beta_acceptance_exit_criteria.md").read_text(encoding="utf-8")

    assert "docs/operations/beta_outcome_report_template.md" in text
    assert "docs/operations/post_beta_evidence_archive_manifest.md" in text
