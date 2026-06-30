from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_consent_rejection_audit import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_consent_rejection_audit_check_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_consent_rejection_audit_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_consent_rejection_audit.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Consent rejection audit check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_consent_rejection_audit_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "popia-consent-rejection-audit-check:" in text
    assert "scripts/check_consent_rejection_audit.py" in text
