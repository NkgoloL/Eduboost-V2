from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_auth_boundary_evidence import REQUIRED_FILES, check_all


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_auth_boundary_required_files_cover_auth_surfaces() -> None:
    assert "app/core/refresh_tokens.py" in REQUIRED_FILES
    assert "app/core/token_revocation.py" in REQUIRED_FILES
    assert "app/security/object_authorization.py" in REQUIRED_FILES
    assert "tests/unit/test_auth_cookie_policy.py" in REQUIRED_FILES


@pytest.mark.unit
def test_auth_boundary_evidence_check_passes_current_repo() -> None:
    assert [result for result in check_all() if not result.ok] == []


@pytest.mark.unit
def test_auth_boundary_evidence_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_auth_boundary_evidence.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Auth boundary evidence check" in result.stdout
