from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_frontend_playwright_scaffold import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_frontend_playwright_scaffold_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_frontend_playwright_scaffold_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_frontend_playwright_scaffold.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Frontend Playwright scaffold check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_frontend_playwright_targets() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "frontend-playwright-scaffold-check:" in text
    assert "frontend-e2e:" in text
