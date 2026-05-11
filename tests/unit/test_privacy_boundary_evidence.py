from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_privacy_boundary_evidence import REQUIRED_FILES, check_all


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_privacy_boundary_required_files_cover_release_surfaces() -> None:
    assert "docs/security/object_authorization.md" in REQUIRED_FILES
    assert "docs/compliance/popia_data_rights.md" in REQUIRED_FILES
    assert "docs/security/audit_event_contracts.md" in REQUIRED_FILES
    assert "scripts/check_popia_consent_audit_evidence.py" in REQUIRED_FILES


@pytest.mark.unit
def test_privacy_boundary_evidence_check_passes_current_repo() -> None:
    failures = [result for result in check_all() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_privacy_boundary_evidence_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_privacy_boundary_evidence.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Privacy boundary evidence check" in result.stdout
