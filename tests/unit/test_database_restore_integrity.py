from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_database_restore_integrity import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_database_restore_integrity_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_database_restore_integrity_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_database_restore_integrity.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Database restore integrity check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_database_restore_integrity_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "database-restore-integrity-check:" in text
    assert "scripts/check_database_restore_integrity.py" in text
