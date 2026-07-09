from app.modules.security_assurance.assurance import (
    build_blocked_security_final_assurance_report,
    build_default_security_final_assurance_report,
    default_security_final_evidence_items,
)


def test_default_security_final_assurance_is_accepted_and_guarded():
    payload = build_default_security_final_assurance_report().to_payload()

    assert payload["prd_id"] == "PRD-6.5-6.9"
    assert payload["accepted"] is True
    assert payload["dast_api_fuzzing_evidence_accepted"] is True
    assert payload["dependency_container_sbom_evidence_accepted"] is True
    assert payload["secret_rotation_rate_limit_abuse_evidence_accepted"] is True
    assert payload["critical_endpoint_authz_negative_tests_accepted"] is True
    assert payload["external_or_independent_review_recorded"] is True
    assert payload["security_signoff_recorded"] is True
    assert payload["prd6_final_reconciliation_recorded"] is True
    assert payload["prd7_implementation_authorised"] is False
    assert payload["live_learner_traffic_authorised"] is False
    assert payload["production_release_authorised"] is False


def test_blocked_security_final_assurance_reports_blockers():
    payload = build_blocked_security_final_assurance_report().to_payload()

    assert payload["accepted"] is False
    assert "final_security_evidence_matrix_incomplete" in payload["blockers"]
    assert "external_or_independent_review_not_recorded" in payload["blockers"]
    assert "security_signoff_not_recorded" in payload["blockers"]


def test_final_evidence_items_are_complete_when_accepted():
    items = default_security_final_evidence_items(accepted=True)

    assert len(items) >= 10
    assert all(item.accepted for item in items)
