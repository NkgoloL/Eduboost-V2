from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_g_closure import COMMANDS, GENERATORS, run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_cluster_g_closure_command_list_is_complete() -> None:
    flattened = "\n".join(" ".join(command) for _, command in (*GENERATORS, *COMMANDS))

    assert "generate_frontend_route_inventory.py" in flattened
    assert "frontend-route-inventory-check" in flattened
    assert "frontend-api-client-inventory-check" in flattened
    assert "frontend-runtime-inventory-check" in flattened
    assert "frontend-playwright-mocked-specs-check" in flattened
    assert "frontend-e2e-runtime-command-check" in flattened
    assert "frontend-e2e-opt-in-workflow-check" in flattened
    assert "frontend-accessibility-static-check" in flattened
    assert "cluster-g-frontend-check" in flattened


@pytest.mark.unit
def test_cluster_g_closure_check_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_g_closure_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_cluster_g_closure.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cluster G closure check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_cluster_g_closure_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "cluster-g-closure-check:" in text
    assert "scripts/check_cluster_g_closure.py" in text
