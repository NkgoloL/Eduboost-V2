from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_terminal_pr_evidence_index import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_terminal_pr_evidence_index_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_terminal_pr_evidence_index_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_terminal_pr_evidence_index.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Terminal PR evidence index check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_terminal_pr_evidence_index_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "terminal-pr-evidence-index-check:" in text
    assert "scripts/check_terminal_pr_evidence_index.py" in text
