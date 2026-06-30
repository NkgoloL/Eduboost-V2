from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_post_merge_evidence_continuity_note import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_post_merge_evidence_continuity_note_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_post_merge_evidence_continuity_note_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_post_merge_evidence_continuity_note.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Post-merge evidence continuity note check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_post_merge_evidence_continuity_note_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "post-merge-evidence-continuity-note-check:" in text
    assert "scripts/check_post_merge_evidence_continuity_note.py" in text
