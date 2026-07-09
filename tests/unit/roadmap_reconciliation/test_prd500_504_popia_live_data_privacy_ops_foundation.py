from scripts.production_readiness.audit_prd500_504_popia_live_data_privacy_ops_foundation import audit


def test_prd500_504_archival_state_remains_valid_after_capture():
    result = audit()

    assert result["authority_valid"] is True
    assert result["valid"] is True
    assert result["previous_prd4_handoff_valid"] is True
    assert result["privacy_live_data_readiness_valid"] is True
    assert result["next_authorised_item"] == "PRD-5.5-5.9"
    assert result["register_next_authorised_item"] in {"PRD-5.5-5.9", "PRD-6"}
    assert result["live_data_processing_impact_assessment_visible"] is True
    assert result["consent_withdrawal_drill_visible"] is True
    assert result["export_deletion_retention_drills_visible"] is True
    assert result["ai_prompt_telemetry_pii_redaction_visible"] is True
    assert result["subprocessor_data_flow_privacy_signoff_visible"] is True
    assert result["prd6_implementation_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False
