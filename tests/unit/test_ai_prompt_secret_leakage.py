from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_ai_prompt_secret_leakage import (
    PROMPT_MARKERS,
    SECRET_MARKERS,
    _is_prompt_literal,
    run_checks,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_ai_prompt_secret_leakage_marker_sets_are_defined() -> None:
    assert "prompt" in PROMPT_MARKERS
    assert "ANTHROPIC_API_KEY" in SECRET_MARKERS
    assert "AZURE_KEY_VAULT_URL" in SECRET_MARKERS


@pytest.mark.unit
def test_ai_prompt_secret_leakage_scopes_to_prompt_literals() -> None:
    assert _is_prompt_literal("Build a lesson prompt for Grade 8 Mathematics") is True
    assert _is_prompt_literal("ANTHROPIC_API_KEY") is False


@pytest.mark.unit
def test_ai_prompt_secret_leakage_check_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_ai_prompt_secret_leakage_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_ai_prompt_secret_leakage.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "AI prompt secret leakage check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_ai_prompt_secret_leakage_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "ai-prompt-secret-leakage-check:" in text
    assert "scripts/check_ai_prompt_secret_leakage.py" in text
