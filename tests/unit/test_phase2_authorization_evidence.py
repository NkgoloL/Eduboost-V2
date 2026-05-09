"""Tests for Phase 2 authorization evidence checker."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_phase2_authorization_evidence.py"

spec = importlib.util.spec_from_file_location("check_phase2_authorization_evidence", SCRIPT)
assert spec is not None
assert spec.loader is not None

checker = importlib.util.module_from_spec(spec)
sys.modules["check_phase2_authorization_evidence"] = checker
spec.loader.exec_module(checker)


@pytest.mark.unit
def test_phase2_authorization_evidence_declares_required_files() -> None:
    required = set(checker.REQUIRED_FILES)

    assert "app/security/object_authorization.py" in required
    assert "app/security/dependencies.py" in required
    assert "tests/integration/test_lesson_generation_authorization.py" in required
    assert "tests/integration/test_diagnostic_items_authorization.py" in required


@pytest.mark.unit
def test_phase2_authorization_evidence_check_passes() -> None:
    failures = [result for result in checker.check_all() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_phase2_authorization_evidence_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Phase 2 authorization evidence check" in result.stdout
