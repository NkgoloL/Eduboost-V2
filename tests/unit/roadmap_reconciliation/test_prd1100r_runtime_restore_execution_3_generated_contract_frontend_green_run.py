from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_3_generated_contract_frontend_green_run import audit


def test_execution_3_authority_is_valid_before_evidence_capture():
    result = audit()
    assert result["authority_valid"] is True
    assert result["valid"] is True
    assert result["generated_contract_frontend_green_run_authority_recorded"] is True
    assert result["generated_contract_frontend_green_run_evidence_recorded"] is True
    assert result["generated_contracts_green"] is False
    assert result["frontend_quality_green"] is False
    assert result["register_next_authorised_item"] == "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3"
