from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_popia_legal_evidence import REQUIRED, check_all

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_popia_legal_required_files_cover_legal_and_data_rights() -> None:
    assert "docs/legal/legal_documents_index.md" in REQUIRED
    assert "docs/compliance/popia_data_rights.md" in REQUIRED
    assert "docs/compliance/subprocessor_register.md" in REQUIRED


@pytest.mark.unit
def test_popia_legal_evidence_passes() -> None:
    assert [r for r in check_all() if not r.ok] == []


@pytest.mark.unit
def test_popia_legal_cli_passes() -> None:
    result = subprocess.run([sys.executable, "scripts/check_popia_legal_evidence.py"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
