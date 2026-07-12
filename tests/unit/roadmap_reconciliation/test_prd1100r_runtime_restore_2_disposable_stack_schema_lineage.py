from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid, assert_current_execution_state
from scripts.production_readiness.audit_prd1100r_runtime_restore_2_disposable_stack_schema_lineage import audit


def test_prd1100r_runtime_restore_2_authority_valid_before_capture() -> None:
    result = audit()
    assert_archival_or_current_valid(result)
    assert_archival_or_current_valid(result)
    assert result["disposable_stack_schema_lineage_authority_recorded"] is True
    assert result["disposable_stack_schema_lineage_evidence_recorded"] is True
    assert result["no_blind_alembic_stamp"] is True
    assert result["controlled_beta_activation_operational_hold"] is True
    assert result["live_learner_traffic_operationally_safe"] is False
    assert_current_execution_state(result)
