from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_learning_evidence import REQUIRED_FILES, check_all


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_learning_evidence_required_files_cover_learning_surfaces() -> None:
    assert "docs/diagnostics/item_contract.md" in REQUIRED_FILES
    assert "app/modules/diagnostics/irt_engine.py" in REQUIRED_FILES
    assert "app/modules/diagnostics/diagnostic_session_service.py" in REQUIRED_FILES
    assert "app/modules/progress/mastery_model.py" in REQUIRED_FILES
    assert "docs/learning_science/learning_evidence.md" in REQUIRED_FILES


@pytest.mark.unit
def test_learning_evidence_check_passes_current_repo() -> None:
    failures = [result for result in check_all() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_learning_evidence_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_learning_evidence.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Learning evidence check" in result.stdout
