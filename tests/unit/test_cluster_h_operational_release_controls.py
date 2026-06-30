from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_operational_release_controls_registered() -> None:
    subprocess.run(
        [sys.executable, "scripts/generate_staging_smoke_evidence_manifest.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [sys.executable, "scripts/generate_beta_signoff_manifest.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_operational_release_controls() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make beta-signoff-manifest" in text
    assert "make beta-signoff-manifest-check" in text
    assert "make beta-rollback-runbook-check" in text
    assert "make post-deploy-staging-smoke-checklist-check" in text
    assert "tests/unit/test_cluster_h_operational_release_controls.py" in text


@pytest.mark.unit
def test_beta_readiness_contract_links_operational_controls() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "beta_release_readiness_contract.md").read_text(encoding="utf-8")

    assert "docs/operations/beta_signoff_manifest.md" in text
    assert "docs/operations/beta_rollback_runbook.md" in text
    assert "docs/operations/post_deploy_staging_smoke_checklist.md" in text
