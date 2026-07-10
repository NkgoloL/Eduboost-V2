from __future__ import annotations

from app.modules.commercial_launch import (
    build_blocked_commercial_runtime_audit_remediation_report,
    build_default_commercial_runtime_audit_remediation_report,
)


def test_commercial_runtime_audit_remediation_default_is_accepted_and_boundaries_closed():
    payload = build_default_commercial_runtime_audit_remediation_report().to_payload()

    assert payload["prd_id"] == "PRD-9.5-9.9"
    assert payload["accepted"] is True
    assert payload["runtime_blockers_remediated"] is True
    assert payload["audit_2026_07_09_reconciled"] is True
    assert payload["billing_launch_authorised"] is False
    assert payload["live_payment_processing_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False
    assert payload["prd10_implementation_authorised"] is False


def test_commercial_runtime_audit_remediation_blocked_state_exposes_blocker():
    payload = build_blocked_commercial_runtime_audit_remediation_report().to_payload()

    assert payload["accepted"] is False
    assert "commercial_runtime_audit_remediation_incomplete" in payload["blockers"]
