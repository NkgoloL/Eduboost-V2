from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_release_readiness_check_passes() -> None:
    subprocess.run(
        [sys.executable, "scripts/generate_staging_smoke_evidence_manifest.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_release_readiness_cli_passes() -> None:
    subprocess.run(
        [sys.executable, "scripts/generate_staging_smoke_evidence_manifest.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [sys.executable, "scripts/check_cluster_h_release_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cluster H release readiness check" in result.stdout


@pytest.mark.unit
def test_cluster_h_workflow_runs_release_readiness_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make staging-smoke-evidence-manifest" in text
    assert "make beta-release-readiness-contract-check" in text
    assert "make staging-smoke-evidence-manifest-check" in text
    assert "make cluster-h-release-readiness-check" in text


@pytest.mark.unit
def test_makefile_exposes_cluster_h_release_readiness_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "cluster-h-release-readiness-check:" in text
    assert "scripts/check_cluster_h_release_readiness.py" in text
