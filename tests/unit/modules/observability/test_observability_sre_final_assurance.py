from app.modules.observability import (
    build_blocked_observability_final_assurance_report,
    build_default_observability_final_assurance_report,
    default_observability_final_evidence_items,
)


def test_default_observability_final_assurance_is_accepted_and_preserves_boundaries():
    payload = build_default_observability_final_assurance_report().to_payload()

    assert payload["prd_id"] == "PRD-7.5-7.9"
    assert payload["source_readiness_prd_id"] == "PRD-7.0-7.4"
    assert payload["accepted"] is True
    assert payload["dashboard_alert_slo_evidence_accepted"] is True
    assert payload["incident_runbook_on_call_evidence_accepted"] is True
    assert payload["backup_restore_rollback_evidence_accepted"] is True
    assert payload["privacy_escalation_support_evidence_accepted"] is True
    assert payload["telemetry_pii_redaction_evidence_accepted"] is True
    assert payload["final_evidence_matrix_accepted"] is True
    assert payload["prd8_implementation_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False
    assert payload["production_release_authorised"] is False


def test_blocked_observability_final_assurance_exposes_blockers():
    payload = build_blocked_observability_final_assurance_report().to_payload()

    assert payload["accepted"] is False
    assert "final_observability_sre_evidence_matrix_incomplete" in payload["blockers"]
    assert "incident_readiness_reconciliation_not_recorded" in payload["blockers"]
    assert "sre_signoff_not_recorded" in payload["blockers"]


def test_default_final_evidence_items_cover_expected_matrix():
    items = default_observability_final_evidence_items()

    assert len(items) >= 10
    assert all(item.accepted for item in items)
