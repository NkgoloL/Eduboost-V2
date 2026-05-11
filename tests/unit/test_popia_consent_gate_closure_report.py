from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "docs" / "security" / "POPIA_CONSENT_GATE_CLOSURE.md"


@pytest.mark.unit
def test_popia_consent_gate_closure_report_exists() -> None:
    assert REPORT.exists()


@pytest.mark.unit
def test_popia_consent_gate_closure_report_has_required_evidence() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "# POPIA Consent Gate Closure Report" in text
    assert "make popia-consent-gate-check" in text
    assert "make audit-contract-check" in text
    assert "make popia-consent-audit-check" in text
    assert "make popia-consent-boundary-check" in text
    assert "rights_exercise_not_active_consent_blocked" in text
    assert "Next Hardening Targets" in text
