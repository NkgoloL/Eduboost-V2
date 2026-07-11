from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_1_runtime_command_frontend_generated_contracts import ROOT, audit


def test_prd1100r_runtime_restore_execution_1_authority_is_valid():
    result = audit(ROOT)
    assert result["authority_valid"] is True
    assert result["runtime_restore_execution_1_authority_recorded"] is True
    assert result["collector_uses_current_python_interpreter"] is True
    assert result["generated_contract_gate_uses_current_interpreter"] is True
    assert result["frontend_conditional_hook_repaired"] is True
    assert result["controlled_beta_activation_operational_hold"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
