from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_frontend_runtime_inventory import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_frontend_runtime_inventory_generation_and_check_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_frontend_runtime_inventory.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_frontend_runtime_inventory_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_frontend_runtime_inventory.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Frontend runtime inventory check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_frontend_runtime_inventory_targets() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "frontend-runtime-inventory:" in text
    assert "frontend-runtime-inventory-check:" in text
