from tests.support.governance_state import assert_archival_or_current_valid, assert_current_execution_state
from scripts.production_readiness.audit_prd1100r_runtime_restore_1_runtime_stack_db_lineage_readiness import audit


def test_prd1100r_runtime_restore_1_authority_is_valid_before_capture() -> None:
    result = audit()
    assert_archival_or_current_valid(result)
    assert_archival_or_current_valid(result)
    assert result["runtime_stack_db_lineage_readiness_authority_recorded"] is True
    assert result["runtime_stack_db_lineage_readiness_evidence_recorded"] is True
    assert_current_execution_state(result)


def test_prd1100r_runtime_restore_1_preserves_release_boundaries() -> None:
    result = audit()
    assert result["false_boundaries_locked"] is True
    assert result["controlled_beta_activation_operational_hold"] is True
    assert result["live_learner_traffic_operationally_safe"] is False
    assert result["production_release_evidence_blocked_until_runtime_baseline_green"] is True
