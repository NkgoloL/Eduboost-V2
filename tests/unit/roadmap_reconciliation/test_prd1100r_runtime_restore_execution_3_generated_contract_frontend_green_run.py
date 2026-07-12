from tests.support.governance_state import assert_archival_or_current_valid, assert_current_execution_state
from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_3_generated_contract_frontend_green_run import audit


def test_execution_3_authority_is_valid_before_evidence_capture():
    result = audit()
    assert_archival_or_current_valid(result)
    assert_archival_or_current_valid(result)
    assert result["generated_contract_frontend_green_run_authority_recorded"] is True
    assert result["generated_contract_frontend_green_run_evidence_recorded"] is True
    assert result["generated_contracts_green"] is False
    assert result["frontend_quality_green"] is False
    assert_current_execution_state(result)
