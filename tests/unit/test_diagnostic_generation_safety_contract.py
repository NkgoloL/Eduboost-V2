from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_diagnostic_generation_safety_contract import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_diagnostic_generation_safety_contract_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_diagnostic_generation_safety_contract_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_diagnostic_generation_safety_contract.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Diagnostic generation safety contract check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_diagnostic_generation_safety_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "diagnostic-generation-safety-check:" in text
    assert "scripts/check_diagnostic_generation_safety_contract.py" in text
