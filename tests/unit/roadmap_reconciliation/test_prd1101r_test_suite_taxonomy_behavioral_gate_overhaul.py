from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid, assert_current_execution_state
from scripts.production_readiness.audit_prd1101r_test_suite_taxonomy_behavioral_gate_overhaul import audit


def test_prd1101r_authority_state_is_valid_before_capture() -> None:
    result = audit()
    assert_archival_or_current_valid(result)
    assert result["taxonomy_valid"] is True
    assert result["governance_sync_valid"] is True
    assert result["separate_test_classes_recorded"] is True
    assert result["product_test_class_recorded"] is True
    assert result["runtime_test_class_recorded"] is True
    assert result["governance_test_class_recorded"] is True
    assert result["advisory_test_class_recorded"] is True
    assert result["false_boundaries_locked"] is True
    assert result["next_authorised_item"] == "PRD-11.2R"
    assert_current_execution_state(result)


def test_prd1101r_blocks_handoff_until_evidence_capture() -> None:
    result = audit()
    assert result["test_suite_taxonomy_evidence_recorded"] is True
    assert result["prd112r_handoff_authorised"] is True
    assert result["next_authorised_item"] == "PRD-11.2R"
    assert_current_execution_state(result)
