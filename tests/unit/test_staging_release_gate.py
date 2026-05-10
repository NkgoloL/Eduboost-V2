from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_staging_release_gate import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_staging_release_gate_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_staging_release_gate_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_staging_release_gate.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Staging release gate check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_staging_release_gate_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "staging-release-gate-check:" in text
    assert "scripts/check_staging_release_gate.py" in text
