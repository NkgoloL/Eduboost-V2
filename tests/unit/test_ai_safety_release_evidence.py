from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_ai_safety_release_evidence import REQUIRED, check_all

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_ai_safety_required_files_cover_llm_pii_schema_and_refusals() -> None:
    assert "app/services/pii_sweep.py" in REQUIRED
    assert "docs/ai/ai_output_schema_contract.md" in REQUIRED
    assert "tests/unit/test_ai_refusal_fixtures.py" in REQUIRED


@pytest.mark.unit
def test_ai_safety_release_evidence_passes() -> None:
    assert [r for r in check_all() if not r.ok] == []


@pytest.mark.unit
def test_ai_safety_release_cli_passes() -> None:
    result = subprocess.run([sys.executable, "scripts/check_ai_safety_release_evidence.py"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
