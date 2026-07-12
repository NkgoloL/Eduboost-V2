from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid, assert_current_execution_state
from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_5_runtime_stack_db_lineage_ready_green import audit


def test_prd1100r_execution_5_authority_valid() -> None:
    result = audit()
    assert_archival_or_current_valid(result)
    assert result["runtime_green_contract_valid"] is True
    assert result["runtime_stack_db_lineage_ready_green_evidence_recorded"] is True
    assert_current_execution_state(result)
