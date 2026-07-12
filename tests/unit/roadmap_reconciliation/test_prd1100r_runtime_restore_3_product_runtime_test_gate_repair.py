from tests.support.governance_state import assert_archival_or_current_valid, assert_current_execution_state
from scripts.production_readiness.audit_prd1100r_runtime_restore_3_product_runtime_test_gate_repair import audit


def test_prd1100r_runtime_restore_3_authority_is_valid_before_capture():
    result = audit()
    assert_archival_or_current_valid(result)
    assert result["product_runtime_gate_contract_valid"] is True
    assert result["product_runtime_test_gate_authority_recorded"] is True
    assert result["product_runtime_test_gate_evidence_recorded"] is True
    assert_current_execution_state(result)


def test_prd1100r_runtime_restore_3_preserves_operational_hold_and_boundaries():
    result = audit()
    assert result["controlled_beta_activation_operational_hold"] is True
    assert result["live_learner_traffic_operationally_safe"] is False
    assert result["production_release_evidence_blocked_until_runtime_baseline_green"] is True
    assert result["false_boundaries_locked"] is True
    assert result["runtime_baseline_green"] is False
    assert result["product_runtime_gate_green"] is False
