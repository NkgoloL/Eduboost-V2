from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_release_hygiene_closeout_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_hygiene_closeout_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make generated-artifact-hygiene-check" in text
    assert "make branch-sync-rebase-checklist-check" in text
    assert "make pr-closeout-evidence-checklist-check" in text
    assert "tests/unit/test_cluster_h_release_hygiene_closeout.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_hygiene_closeout_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")

    assert "docs/operations/generated_artifact_hygiene_contract.md" in text
    assert "docs/operations/branch_sync_rebase_checklist.md" in text
    assert "docs/operations/pr_closeout_evidence_checklist.md" in text


@pytest.mark.unit
def test_gitignore_excludes_generated_release_noise() -> None:
    text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "coverage.xml" in text
    assert ".pytest_cache/" in text
    assert "playwright-report/" in text
