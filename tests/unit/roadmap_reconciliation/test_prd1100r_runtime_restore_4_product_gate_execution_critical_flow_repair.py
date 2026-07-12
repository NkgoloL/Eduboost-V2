from __future__ import annotations

from scripts.production_readiness.audit_prd1100r_runtime_restore_4_product_gate_execution_critical_flow_repair import audit


def test_runtime_restore_4_authority_valid_before_evidence_capture() -> None:
    result = audit()
    assert result["authority_valid"] is True
    assert result["valid"] is True
    assert result["product_gate_execution_contract_valid"] is True
    assert result["critical_product_flows_recorded"] is True
    assert result["positive_and_negative_flow_evidence_required"] is True
    assert result["independent_command_outputs_required"] is True
    assert result["presence_only_flow_evidence_forbidden"] is True
    assert result["false_boundaries_locked"] is True
    assert result["register_next_authorised_item"] == "PRD-11.0R.RUNTIME-RESTORE-4"


def test_runtime_restore_4_keeps_release_boundaries_locked() -> None:
    result = audit()
    assert result["runtime_baseline_green"] is False
    assert result["product_gate_green"] is False
    assert result["controlled_beta_activation_operational_hold"] is True
    assert result["live_learner_traffic_operationally_safe"] is False
    assert result["production_release_evidence_blocked_until_runtime_baseline_green"] is True
