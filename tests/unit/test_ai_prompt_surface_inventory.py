from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_ai_prompt_surface_inventory import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_ai_prompt_surface_inventory_generation_and_check_pass() -> None:
    gen = subprocess.run(
        [sys.executable, "scripts/generate_ai_prompt_surface_inventory.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert gen.returncode == 0, gen.stdout + gen.stderr

    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_ai_prompt_surface_inventory_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_ai_prompt_surface_inventory.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "AI prompt surface inventory check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_prompt_surface_inventory_targets() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "ai-prompt-surface-inventory:" in text
    assert "ai-prompt-surface-inventory-check:" in text
