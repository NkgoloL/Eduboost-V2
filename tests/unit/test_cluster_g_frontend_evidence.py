from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_g_frontend_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-g-frontend.yml"


@pytest.mark.unit
def test_cluster_g_frontend_evidence_passes() -> None:
    subprocess.run(
        [sys.executable, "scripts/generate_frontend_route_inventory.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_g_frontend_cli_passes() -> None:
    subprocess.run(
        [sys.executable, "scripts/generate_frontend_route_inventory.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [sys.executable, "scripts/check_cluster_g_frontend_evidence.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cluster G frontend evidence check" in result.stdout


@pytest.mark.unit
def test_cluster_g_workflow_runs_frontend_evidence_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make frontend-route-inventory" in text
    assert "make frontend-route-inventory-check" in text
    assert "make learner-vertical-journey-contract-check" in text
    assert "make cluster-g-frontend-check" in text


@pytest.mark.unit
def test_makefile_exposes_cluster_g_frontend_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "cluster-g-frontend-check:" in text
    assert "scripts/check_cluster_g_frontend_evidence.py" in text
