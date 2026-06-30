from __future__ import annotations

import subprocess
import sys

import pytest

from scripts.generate_phase2_authorization_closure_report import REPORT, render


@pytest.mark.unit
def test_phase2_closure_report_renders_core_sections() -> None:
    output = render()

    assert "# Phase 2 Authorization Closure Report" in output
    assert "## Route Matrix Summary" in output
    assert "## Key Evidence" in output
    assert "## Verification Commands" in output
    assert "## Closure Status" in output


@pytest.mark.unit
def test_phase2_closure_report_file_exists_after_generation() -> None:
    assert REPORT.exists()
    text = REPORT.read_text(encoding="utf-8")
    assert "Phase 2 Authorization Closure Report" in text


@pytest.mark.unit
def test_phase2_closure_report_script_runs_directly() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_phase2_authorization_closure_report.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "PHASE2_AUTHORIZATION_CLOSURE.md" in result.stdout
