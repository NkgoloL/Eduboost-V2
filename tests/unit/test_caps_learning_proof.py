from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_caps_learning_proof import REQUIRED, check_all

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_caps_learning_required_files_cover_caps_item_bank_and_mastery() -> None:
    assert "docs/caps/grade4_maths_coverage_matrix.md" in REQUIRED
    assert "docs/diagnostics/item_contract.md" in REQUIRED
    assert "tests/unit/modules/progress/test_mastery_model.py" in REQUIRED


@pytest.mark.unit
def test_caps_learning_proof_passes() -> None:
    assert [r for r in check_all() if not r.ok] == []


@pytest.mark.unit
def test_caps_learning_cli_passes() -> None:
    result = subprocess.run([sys.executable, "scripts/check_caps_learning_proof.py"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
