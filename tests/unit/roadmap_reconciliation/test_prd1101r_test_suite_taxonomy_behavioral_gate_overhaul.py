from __future__ import annotations

from scripts.production_readiness.audit_prd1101r_test_suite_taxonomy_behavioral_gate_overhaul import audit


def test_prd1101r_authority_state_is_valid_before_capture() -> None:
    result = audit()
    assert result["authority_valid"] is True
    assert result["taxonomy_valid"] is True
    assert result["governance_sync_valid"] is True
    assert result["separate_test_classes_recorded"] is True
    assert result["product_test_class_recorded"] is True
    assert result["runtime_test_class_recorded"] is True
    assert result["governance_test_class_recorded"] is True
    assert result["advisory_test_class_recorded"] is True
    assert result["false_boundaries_locked"] is True
    assert result["register_next_authorised_item"] == "PRD-11.1R"
    assert result["production_register_next_authorised_item"] == "PRD-11.1R"
    assert result["valid"] is False


def test_prd1101r_blocks_handoff_until_evidence_capture() -> None:
    result = audit()
    assert result["test_suite_taxonomy_evidence_recorded"] is False
    assert result["prd112r_handoff_authorised"] is False
    assert result["next_authorised_item"] == "PRD-11.1R"
