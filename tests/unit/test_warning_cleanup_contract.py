from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_warning_cleanup_static_check_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_warning_cleanup.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_pytest_ini_restores_hypothesis_ignore():
    text = (ROOT / "pytest.ini").read_text(encoding="utf-8")
    assert ".hypothesis" in text
    assert "tests/legacy" in text


def test_warning_cleanup_register_tracks_known_warnings():
    text = (ROOT / "docs/release/warning_cleanup_register.md").read_text(encoding="utf-8")
    assert "AsyncMockMixin" in text
    assert "Hypothesis" in text
    assert "Redis asyncio connection cleanup" in text


def test_makefile_contains_warning_cleanup_target():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "warning-cleanup-check:" in text
