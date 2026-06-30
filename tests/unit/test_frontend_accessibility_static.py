from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_frontend_accessibility_static import (
    BAD_BUTTON_PATTERN,
    BAD_IMAGE_PATTERN,
    run_checks,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_accessibility_static_patterns_detect_basic_issues() -> None:
    assert BAD_IMAGE_PATTERN.search("<img src='x.png'>") is not None
    assert BAD_IMAGE_PATTERN.search("<img src='x.png' alt='Example'>") is None
    assert BAD_BUTTON_PATTERN.search("<button></button>") is not None


@pytest.mark.unit
def test_frontend_accessibility_static_check_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_frontend_accessibility_static_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_frontend_accessibility_static.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Frontend accessibility static check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_frontend_accessibility_static_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "frontend-accessibility-static-check:" in text
    assert "scripts/check_frontend_accessibility_static.py" in text
