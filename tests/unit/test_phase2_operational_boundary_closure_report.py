from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "docs" / "security" / "PHASE2_AUTHORIZATION_CLOSURE.md"


@pytest.mark.unit
def test_closure_report_includes_operational_boundary_hardening() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "## Operational Auth Boundary Hardening" in text
    assert "dev_session_environment_gate.md" in text
    assert "consent_renewal_admin_auth_boundary.md" in text
    assert "ether_onboarding_questions_auth_boundary.md" in text
    assert "Operational boundary hardening stamp:" in text
