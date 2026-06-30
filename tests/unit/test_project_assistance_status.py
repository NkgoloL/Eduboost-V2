from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.project_assistance_status import LANES, build_report


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_project_assistance_has_five_lanes() -> None:
    assert len(LANES) == 5
    assert [lane.number for lane in LANES] == [1, 2, 3, 4, 5]


@pytest.mark.unit
def test_project_assistance_report_names_all_lanes() -> None:
    report = build_report()

    assert "Project Assistance Status" in report
    for lane in LANES:
        assert lane.name in report
        assert lane.done_when in report


@pytest.mark.unit
def test_project_assistance_report_check_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/project_assistance_status.py", "--check"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Project assistance status is current" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_project_assistance_targets() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "project-assistance-status:" in text
    assert "project-assistance-status-check:" in text
    assert "scripts/project_assistance_status.py" in text
