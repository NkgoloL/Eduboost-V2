from app.modules.content_quality.readiness import (
    CAPS_STRANDS,
    ContentQualityReadinessInputs,
    build_content_quality_readiness_report,
    build_default_grade4_maths_readiness_report,
)


def test_default_grade4_maths_readiness_report_is_ready_and_boundary_safe():
    payload = build_default_grade4_maths_readiness_report().to_payload()

    assert payload["prd_id"] == "PRD-4.0-4.4"
    assert payload["ready"] is True
    assert payload["grade"] == 4
    assert payload["subject"] == "Mathematics"
    assert len(payload["strand_readiness"]) == len(CAPS_STRANDS)
    assert payload["caps_coverage_complete"] is True
    assert payload["bias_language_accessibility_ready"] is True
    assert payload["misconception_remediation_ready"] is True
    assert payload["production_release_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False
    assert payload["prd5_implementation_authorised"] is False


def test_missing_reviews_produce_blockers_and_next_actions():
    payload = build_content_quality_readiness_report(ContentQualityReadinessInputs()).to_payload()

    assert payload["ready"] is False
    assert "educator_reviewed_item_bank_missing" in payload["blockers"]
    assert "caps_coverage_matrix_incomplete" in payload["blockers"]
    assert "bias_language_accessibility_review_incomplete" in payload["blockers"]
    assert all(action.startswith("resolve_") for action in payload["recommended_next_actions"])
