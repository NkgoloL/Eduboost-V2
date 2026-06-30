from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_e_closure import COMMANDS, run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_cluster_e_closure_command_list_is_complete() -> None:
    flattened = "\n".join(" ".join(command) for _, command in COMMANDS)

    assert "database-backup-contract-check" in flattened
    assert "database-restore-drill-docs-check" in flattened
    assert "database-backup-dry-run" in flattened
    assert "database-restore-dry-run" in flattened
    assert "database-backup-manifest" in flattened
    assert "database-restore-evidence" in flattened
    assert "database-backup-integrity-check" in flattened
    assert "database-restore-integrity-check" in flattened
    assert "cluster-e-data-resilience-check" in flattened


@pytest.mark.unit
def test_cluster_e_closure_check_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_e_closure_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_cluster_e_closure.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cluster E closure check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_cluster_e_closure_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "cluster-e-closure-check:" in text
    assert "scripts/check_cluster_e_closure.py" in text
