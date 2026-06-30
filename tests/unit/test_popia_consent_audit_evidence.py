from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_popia_consent_audit_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_popia_consent_audit_evidence_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_popia_consent_audit_evidence_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_popia_consent_audit_evidence.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "POPIA consent/audit evidence check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_popia_consent_audit_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "popia-consent-audit-check:" in text
    assert "scripts/check_popia_consent_audit_evidence.py" in text


@pytest.mark.unit
def test_ether_onboarding_evidence_uses_boundary_not_gate_wording() -> None:
    checker = REPO_ROOT / "scripts" / "check_popia_consent_audit_evidence.py"
    source = checker.read_text(encoding="utf-8")

    assert "Ether Onboarding Consent Boundary" in source
    assert "authenticated_catalog_boundary" in source
    assert "Ether Onboarding Consent Gate" not in source
