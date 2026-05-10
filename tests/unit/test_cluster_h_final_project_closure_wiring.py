from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_final_project_closure_wiring_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_final_project_closure_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make release-artifact-retention-contract-check" in text
    assert "make beta-release-final-checklist-check" in text
    assert "make project-release-closure-index-check" in text
    assert "tests/unit/test_cluster_h_final_project_closure_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_final_project_closure_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")

    assert "docs/operations/release_artifact_retention_contract.md" in text
    assert "docs/operations/beta_release_final_checklist.md" in text
    assert "docs/operations/project_release_closure_index.md" in text


@pytest.mark.unit
def test_project_evidence_index_links_final_project_closure() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "project_evidence_index.md").read_text(encoding="utf-8")

    assert "docs/operations/project_release_closure_index.md" in text
