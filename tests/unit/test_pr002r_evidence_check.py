"""Tests for the PR-002R evidence checker."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_pr002r_evidence.py"

spec = importlib.util.spec_from_file_location("check_pr002r_evidence", SCRIPT)
assert spec is not None
assert spec.loader is not None

check_pr002r_evidence = importlib.util.module_from_spec(spec)
sys.modules["check_pr002r_evidence"] = check_pr002r_evidence
spec.loader.exec_module(check_pr002r_evidence)

REQUIRED_FILES = check_pr002r_evidence.REQUIRED_FILES
CONTENT_REQUIREMENTS = check_pr002r_evidence.CONTENT_REQUIREMENTS
check_all = check_pr002r_evidence.check_all


@pytest.mark.unit
def test_pr002r_evidence_required_files_are_declared() -> None:
    assert "docs/openapi.json" in REQUIRED_FILES
    assert "docs/route_inventory.md" in REQUIRED_FILES
    assert "scripts/check_runtime_entrypoints.py" in REQUIRED_FILES
    assert "tests/unit/test_pr002r_governance_contract.py" in REQUIRED_FILES


@pytest.mark.unit
def test_pr002r_evidence_content_requirements_cover_core_artifacts() -> None:
    assert ".github/pull_request_template.md" in CONTENT_REQUIREMENTS
    assert "docs/release/PR-002R_EVIDENCE.md" in CONTENT_REQUIREMENTS
    assert "docs/route_inventory.md" in CONTENT_REQUIREMENTS
    assert "Makefile" in CONTENT_REQUIREMENTS


@pytest.mark.unit
def test_pr002r_evidence_check_passes_current_repository_state() -> None:
    results = check_all()
    failures = [result for result in results if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_pr002r_evidence_check_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PR-002R evidence check" in result.stdout
    assert "PASS" in result.stdout
