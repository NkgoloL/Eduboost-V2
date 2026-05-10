from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_d_closure import COMMANDS, run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_cluster_d_closure_command_list_is_complete() -> None:
    flattened = "\n".join(" ".join(command) for _, command in COMMANDS)

    assert "environment-security-check" in flattened
    assert "production-secret-placeholder-check" in flattened
    assert "dev-only-endpoint-check" in flattened
    assert "deployment-readiness-docs-check" in flattened
    assert "cluster-d-ci-check" in flattened
    assert "test_production_key_vault_behavior.py" in flattened


@pytest.mark.unit
def test_cluster_d_closure_check_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_d_closure_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_cluster_d_closure.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cluster D closure check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_cluster_d_closure_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "cluster-d-closure-check:" in text
    assert "scripts/check_cluster_d_closure.py" in text
