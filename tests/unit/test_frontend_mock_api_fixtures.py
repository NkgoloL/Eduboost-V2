from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_frontend_mock_api_fixtures import ERROR_FIXTURES, SUCCESS_FIXTURES, run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_frontend_mock_api_fixture_sets_are_complete() -> None:
    assert "learner_dashboard_success.json" in SUCCESS_FIXTURES
    assert "parent_dashboard_success.json" in SUCCESS_FIXTURES
    assert "consent_denied_error.json" in ERROR_FIXTURES
    assert "authorization_denied_error.json" in ERROR_FIXTURES


@pytest.mark.unit
def test_frontend_mock_api_fixtures_pass() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_frontend_mock_api_fixtures_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_frontend_mock_api_fixtures.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Frontend mock API fixture check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_frontend_mock_api_fixture_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "frontend-mock-api-fixture-check:" in text
    assert "scripts/check_frontend_mock_api_fixtures.py" in text
