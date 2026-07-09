from app.modules.privacy_ops.readiness import (
    DATA_FLOW_AREAS,
    PrivacyLiveDataReadinessInputs,
    build_default_privacy_live_data_readiness_report,
    build_privacy_live_data_readiness_report,
)


def test_default_privacy_live_data_readiness_is_ready_and_boundary_safe():
    payload = build_default_privacy_live_data_readiness_report().to_payload()

    assert payload["prd_id"] == "PRD-5.0-5.4"
    assert payload["ready"] is True
    assert payload["data_flow_matrix_ready"] is True
    assert payload["consent_withdrawal_drill_proven"] is True
    assert payload["export_drill_proven"] is True
    assert payload["deletion_drill_proven"] is True
    assert payload["retention_drill_proven"] is True
    assert payload["ai_prompt_pii_redaction_proven"] is True
    assert payload["telemetry_pii_redaction_proven"] is True
    assert payload["subprocessor_data_flow_confirmed"] is True
    assert payload["privacy_signoff_path_visible"] is True
    assert len(payload["data_flow_controls"]) == len(DATA_FLOW_AREAS)
    assert "prepare_prd5_final_privacy_assurance_handoff" in payload["recommended_next_actions"]
    assert payload["production_release_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False
    assert payload["prd6_implementation_authorised"] is False


def test_blocked_privacy_live_data_readiness_preserves_blockers():
    payload = build_privacy_live_data_readiness_report(PrivacyLiveDataReadinessInputs()).to_payload()

    assert payload["ready"] is False
    assert "live_data_processing_impact_assessment_missing" in payload["blockers"]
    assert "consent_withdrawal_drill_missing" in payload["blockers"]
    assert "export_drill_missing" in payload["blockers"]
    assert "ai_prompt_telemetry_pii_redaction_missing" in payload["blockers"]
    assert all(action.startswith("resolve_") for action in payload["recommended_next_actions"])
