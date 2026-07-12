from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd500_504_popia_live_data_privacy_ops_foundation import audit


def test_prd500_504_archival_state_remains_valid_after_capture():
    result = audit()

    assert_archival_or_current_valid(result)
    assert_archival_or_current_valid(result)
    assert result["privacy_live_data_readiness_valid"] is True
    assert_historical_next_with_current_execution(result, "PRD-5.5-5.9")
    assert result["live_data_processing_impact_assessment_visible"] is True
    assert result["consent_withdrawal_drill_visible"] is True
    assert result["export_deletion_retention_drills_visible"] is True
    assert result["ai_prompt_telemetry_pii_redaction_visible"] is True
    assert result["subprocessor_data_flow_privacy_signoff_visible"] is True
    assert result["prd6_implementation_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False
