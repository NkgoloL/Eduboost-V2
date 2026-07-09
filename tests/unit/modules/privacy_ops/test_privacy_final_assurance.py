from app.modules.privacy_ops.assurance import (
    AUDIT_REPORT_ID,
    FINAL_ASSURANCE_CRITERIA,
    build_blocked_privacy_final_assurance_report,
    build_default_privacy_final_assurance_report,
    default_audit_crosswalk_items,
)


def test_default_privacy_final_assurance_is_accepted_and_boundary_safe():
    payload = build_default_privacy_final_assurance_report().to_payload()

    assert payload["prd_id"] == "PRD-5.5-5.9"
    assert payload["source_readiness_prd_id"] == "PRD-5.0-5.4"
    assert payload["audit_report_id"] == AUDIT_REPORT_ID
    assert payload["accepted"] is True
    assert payload["prd5_sequence_complete"] is True
    assert payload["prd6_handoff_ready"] is True
    assert payload["audit_2026_07_09_crosswalk_reconciled"] is True
    assert payload["privacy_signoff_recorded"] is True
    assert payload["prd5_final_reconciliation_recorded"] is True
    assert "handoff_to_prd6_security_assurance_external_review" in payload["recommended_next_actions"]
    assert len(FINAL_ASSURANCE_CRITERIA) >= 5
    assert len(payload["audit_crosswalk"]) >= 7
    assert payload["prd6_implementation_authorised"] is False
    assert payload["production_release_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False


def test_blocked_privacy_final_assurance_preserves_blockers():
    payload = build_blocked_privacy_final_assurance_report().to_payload()

    assert payload["accepted"] is False
    assert "prd5_live_data_readiness_incomplete" in payload["blockers"]
    assert "privacy_signoff_not_recorded" in payload["blockers"]
    assert "audit_2026_07_09_crosswalk_not_reconciled" in payload["blockers"]
    assert all(action.startswith("resolve_") for action in payload["recommended_next_actions"])


def test_audit_crosswalk_maps_to_existing_prd_ladder():
    payload = [item.to_payload() for item in default_audit_crosswalk_items()]
    owning_prds = {item["owning_prd"] for item in payload}

    assert "PRD-5" in owning_prds
    assert "PRD-6" in owning_prds
    assert "PRD-7" in owning_prds
    assert "PRD-8" in owning_prds
    assert all(item["reconciled"] for item in payload)
