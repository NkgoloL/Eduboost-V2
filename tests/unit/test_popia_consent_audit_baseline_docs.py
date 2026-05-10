from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
DOC = REPO_ROOT / "docs" / "security" / "POPIA_CONSENT_AUDIT_BASELINE.md"


@pytest.mark.unit
def test_popia_consent_audit_baseline_doc_exists() -> None:
    assert DOC.exists()


@pytest.mark.unit
def test_popia_consent_audit_baseline_doc_has_core_sections() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "# POPIA Consent and Audit Baseline" in text
    assert "app/modules/consent/service.py" in text
    assert "app/core/audit.py" in text
    assert "scripts/generate_consent_gate_inventory.py" in text
    assert "scripts/check_audit_event_contracts.py" in text
    assert "Next Hardening Targets" in text
