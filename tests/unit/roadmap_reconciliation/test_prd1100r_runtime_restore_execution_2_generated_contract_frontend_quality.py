from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid, assert_current_execution_state
from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_2_generated_contract_frontend_quality import audit


def test_prd1100r_runtime_restore_execution_2_uses_completed_digest_bound_review() -> None:
    result = audit()
    assert_archival_or_current_valid(result)
    assert result["generated_frontend_contract_valid"] is True
    assert result["authority_valid"] is True
    assert result["generated_contracts_green"] is True
    assert result["frontend_quality_green"] is True
    assert_current_execution_state(result)


def test_prd1100r_runtime_restore_execution_2_source_repairs_recorded() -> None:
    result = audit()
    checks = result["source_checks"]
    assert checks["gate_runner_uses_current_python_interpreter"] is True
    assert checks["generated_contract_read_only_check_recorded"] is True
    assert checks["frontend_release_quality_script_recorded"] is True
    assert checks["frontend_quality_uses_existing_test_script"] is True
    assert checks["generated_contract_commands_have_python_fallback"] is True
