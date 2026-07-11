from __future__ import annotations

from scripts.production_readiness.audit_prd1100r_runtime_restore_6_final_true_state_baseline_handoff import audit


def test_prd1100r_runtime_restore_6_authority_is_valid_before_capture() -> None:
    result = audit()
    assert result["authority_valid"] is True
    assert result["final_true_state_baseline_contract_valid"] is True
    assert result["final_true_state_baseline_handoff_authority_recorded"] is True
    assert result["runtime_baseline_required_green_for_handoff"] is True
    assert result["independent_command_outputs_required"] is True


def test_prd1100r_runtime_restore_6_does_not_claim_green_handoff() -> None:
    result = audit()
    assert result["runtime_baseline_green"] is False
    assert result["product_gate_green"] is False
    assert result["coverage_gate_green"] is False
    assert result["controlled_handoff_to_prd1100_1104_authorised"] is False
    assert result["false_boundaries_locked"] is True
