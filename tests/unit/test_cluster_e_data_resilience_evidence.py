from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_e_data_resilience_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-e-data-resilience.yml"


@pytest.mark.unit
def test_cluster_e_data_resilience_evidence_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_e_data_resilience_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_cluster_e_data_resilience_evidence.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cluster E data-resilience evidence check" in result.stdout


@pytest.mark.unit
def test_cluster_e_workflow_runs_data_resilience_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make database-backup-contract-check" in text
    assert "make database-restore-drill-docs-check" in text
    assert "make cluster-e-data-resilience-check" in text


@pytest.mark.unit
def test_makefile_exposes_cluster_e_data_resilience_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "cluster-e-data-resilience-check:" in text
    assert "scripts/check_cluster_e_data_resilience_evidence.py" in text
