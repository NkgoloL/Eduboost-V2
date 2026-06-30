from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_popia_consent_audit_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_assessment_and_onboarding_consent_evidence_is_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_consent_allowlist_refreshed_after_assessment_and_onboarding_wiring() -> None:
    allowlist = (REPO_ROOT / "docs" / "security" / "popia_consent_gate_allowlist.txt").read_text(encoding="utf-8")

    assert "app/api_v2_routers/assessments.py::submit_attempt" not in allowlist
    assert "app/api_v2_routers/onboarding.py::submit_onboarding" not in allowlist
