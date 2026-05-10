from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_frontend_journey_fixtures import REQUIRED_FIXTURES, run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_frontend_journey_fixture_list_is_complete() -> None:
    assert "learner_journey_fixture.json" in REQUIRED_FIXTURES
    assert "parent_journey_fixture.json" in REQUIRED_FIXTURES


@pytest.mark.unit
def test_frontend_journey_fixtures_pass() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_frontend_journey_fixtures_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_frontend_journey_fixtures.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Frontend journey fixture check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_frontend_journey_fixture_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "frontend-journey-fixture-check:" in text
    assert "scripts/check_frontend_journey_fixtures.py" in text
