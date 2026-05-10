from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_d_ci_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-d-ci.yml"


@pytest.mark.unit
def test_cluster_d_ci_evidence_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_d_ci_evidence_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_cluster_d_ci_evidence.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cluster D CI/deployment evidence check" in result.stdout


@pytest.mark.unit
def test_cluster_d_workflow_runs_environment_and_deployment_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make environment-security-check" in text
    assert "make deployment-readiness-docs-check" in text
    assert "make cluster-d-ci-check" in text


@pytest.mark.unit
def test_makefile_exposes_cluster_d_ci_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "cluster-d-ci-check:" in text
    assert "scripts/check_cluster_d_ci_evidence.py" in text
