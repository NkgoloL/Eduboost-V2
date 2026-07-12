from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd800_804_performance_scale_cost_execution_foundation import audit


def test_prd800_804_authority_and_evidence_state_are_valid():
    result = audit()

    assert_archival_or_current_valid(result)
    assert result["previous_prd7_handoff_valid"] is True
    assert result["performance_scale_cost_readiness_valid"] is True
    assert result["load_test_readiness_defined"] is True
    assert result["runtime_kg_query_performance_defined"] is True
    assert result["llm_cost_simulation_defined"] is True
    assert result["prd9_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    assert result["performance_scale_cost_foundation_recorded"] is True
    assert result["performance_scale_cost_evidence_recorded"] is True
    assert_historical_next_with_current_execution(result, "PRD-8.5-8.9")
