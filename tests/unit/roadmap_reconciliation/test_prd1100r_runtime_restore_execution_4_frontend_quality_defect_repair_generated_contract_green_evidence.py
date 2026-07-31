from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_4_frontend_quality_defect_repair_generated_contract_green_evidence import audit


def test_prd1100r_execution_4_authority_valid_before_evidence():
    result = audit()
    assert result["authority_valid"] is True
    assert result["valid"] is True
    assert result["frontend_quality_defect_repair_authority_recorded"] is True
    assert result["frontend_quality_defect_repair_evidence_recorded"] is True
    assert result["generated_contracts_green"] is True
    assert result["frontend_quality_green"] is True
    assert result["register_next_authorised_item"] == "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"
