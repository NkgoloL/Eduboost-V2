from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_terminal_handoff_closure_note import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_terminal_handoff_closure_note_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_terminal_handoff_closure_note_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_terminal_handoff_closure_note.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Terminal handoff closure note check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_terminal_handoff_closure_note_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "terminal-handoff-closure-note-check:" in text
    assert "scripts/check_terminal_handoff_closure_note.py" in text
