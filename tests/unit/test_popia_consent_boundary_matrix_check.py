from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_popia_consent_boundary_matrix import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_popia_consent_boundary_matrix_check_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_popia_consent_boundary_matrix_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_popia_consent_boundary_matrix.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "POPIA consent-boundary matrix check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_popia_consent_boundary_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "popia-consent-boundary-check:" in text
    assert "scripts/generate_popia_consent_boundary_matrix.py" in text
    assert "scripts/check_popia_consent_boundary_matrix.py" in text
