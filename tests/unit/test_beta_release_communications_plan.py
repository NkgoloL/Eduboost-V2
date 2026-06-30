from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_beta_release_communications_plan import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_beta_release_communications_plan_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_beta_release_communications_plan_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_beta_release_communications_plan.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Beta release communications plan check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_beta_release_communications_plan_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "beta-release-communications-plan-check:" in text
    assert "scripts/check_beta_release_communications_plan.py" in text
