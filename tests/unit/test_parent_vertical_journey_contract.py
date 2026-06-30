from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_parent_vertical_journey_contract import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_parent_vertical_journey_contract_passes() -> None:
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
def test_parent_vertical_journey_contract_cli_passes() -> None:
    subprocess.run(
        [sys.executable, "scripts/generate_frontend_route_inventory.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [sys.executable, "scripts/check_parent_vertical_journey_contract.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Parent vertical journey contract check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_parent_vertical_journey_contract_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "parent-vertical-journey-contract-check:" in text
    assert "scripts/check_parent_vertical_journey_contract.py" in text
