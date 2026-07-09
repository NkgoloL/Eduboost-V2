from app.modules.content_quality.acceptance import (
    ACCEPTANCE_CRITERIA,
    build_content_quality_final_acceptance_report,
    build_default_grade4_maths_content_quality_acceptance_report,
)
from app.modules.content_quality.readiness import ContentQualityReadinessInputs


def test_default_content_quality_acceptance_is_accepted_and_boundary_safe():
    payload = build_default_grade4_maths_content_quality_acceptance_report().to_payload()

    assert payload["prd_id"] == "PRD-4.5-4.9"
    assert payload["source_readiness_prd_id"] == "PRD-4.0-4.4"
    assert payload["accepted"] is True
    assert payload["prd4_sequence_complete"] is True
    assert payload["prd5_handoff_ready"] is True
    assert len(payload["acceptance_criteria"]) == len(ACCEPTANCE_CRITERIA)
    assert "handoff_to_prd5_privacy_live_data_operations" in payload["recommended_next_actions"]
    assert payload["production_release_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False
    assert payload["prd5_implementation_authorised"] is False


def test_blocked_content_quality_acceptance_preserves_blockers():
    payload = build_content_quality_final_acceptance_report(ContentQualityReadinessInputs()).to_payload()

    assert payload["accepted"] is False
    assert payload["prd5_handoff_ready"] is False
    assert "educator_reviewed_item_bank_missing" in payload["blockers"]
    assert "caps_coverage_matrix_incomplete" in payload["blockers"]
    assert all(action.startswith("resolve_") for action in payload["recommended_next_actions"])
