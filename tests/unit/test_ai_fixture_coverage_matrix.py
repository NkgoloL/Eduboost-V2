from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_ai_fixture_coverage_matrix import REQUIRED_FIXTURES, run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_ai_fixture_coverage_matrix_lists_required_fixtures() -> None:
    assert "tests/fixtures/ai/safe_lesson_output.json" in REQUIRED_FIXTURES
    assert "tests/fixtures/ai/refusals/hidden_prompt_refusal.json" in REQUIRED_FIXTURES


@pytest.mark.unit
def test_ai_fixture_coverage_matrix_check_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_ai_fixture_coverage_matrix_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_ai_fixture_coverage_matrix.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "AI fixture coverage matrix check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_ai_fixture_coverage_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "ai-fixture-coverage-check:" in text
    assert "scripts/check_ai_fixture_coverage_matrix.py" in text
