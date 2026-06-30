from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "popia-consent-audit.yml"


@pytest.mark.unit
def test_popia_consent_audit_workflow_exists() -> None:
    assert WORKFLOW.exists()


@pytest.mark.unit
def test_popia_consent_audit_workflow_has_required_commands() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "name: POPIA Consent Audit" in text
    assert "pull_request:" in text
    assert "master" in text
    assert "release/**" in text
    assert "make audit-contract-check" in text
    assert "make popia-consent-gate-check" in text
    assert "test_consent_gate_inventory_check.py" in text
    assert "test_audit_event_contracts.py" in text
