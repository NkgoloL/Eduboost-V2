from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_api_envelope_error_contract import BASELINE_ERROR_CODES, REQUIRED_FILES, check_all


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_api_contract_required_files_cover_envelope_and_error_surfaces() -> None:
    assert "app/domain/api_v2_models.py" in REQUIRED_FILES
    assert "app/core/exceptions.py" in REQUIRED_FILES
    assert "docs/error_contract.md" in REQUIRED_FILES
    assert "docs/api_envelope_contract.md" in REQUIRED_FILES


@pytest.mark.unit
def test_error_contract_declares_all_baseline_codes() -> None:
    text = (REPO_ROOT / "docs/error_contract.md").read_text(encoding="utf-8")

    for code in BASELINE_ERROR_CODES:
        assert f"`{code}`" in text


@pytest.mark.unit
def test_api_envelope_error_contract_check_passes_current_repo() -> None:
    failures = [result for result in check_all() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_api_envelope_error_contract_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_api_envelope_error_contract.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "API envelope/error contract check" in result.stdout
