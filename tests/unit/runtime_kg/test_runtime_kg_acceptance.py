from app.services.runtime_kg.acceptance import build_runtime_kg_acceptance_report
from app.services.runtime_kg.feature_flags import RuntimeKGFeatureFlags


def test_runtime_kg_final_acceptance_report_preserves_opt_in_boundary():
    report = build_runtime_kg_acceptance_report()
    payload = report.to_payload()

    assert payload["accepted"] is True
    assert payload["prd_id"] == "PRD-2.7-2.9"
    assert payload["runtime_kg_enabled_by_default"] is False
    assert payload["next_authorised_item"] == "PRD-3"
    assert payload["prd3_implementation_authorised"] is False
    assert {check["name"] for check in payload["checks"]} >= {
        "runtime_kg_disabled_by_default",
        "projection_payload_available",
        "rollback_payload_available",
        "prd3_handoff_only",
    }


def test_runtime_kg_acceptance_report_fails_if_flag_is_forced_on():
    report = build_runtime_kg_acceptance_report(RuntimeKGFeatureFlags(enabled=True))
    payload = report.to_payload()

    assert payload["accepted"] is False
    assert payload["runtime_kg_enabled_by_default"] is True
