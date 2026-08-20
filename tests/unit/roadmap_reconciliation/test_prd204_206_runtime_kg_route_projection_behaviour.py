from tests.support.governance_state import assert_archival_or_current_valid
from scripts.production_readiness.audit_prd204_206_runtime_kg_route_projection_behaviour import audit


def test_prd204_206_evidence_is_fully_recorded():
    result = audit()
    assert_archival_or_current_valid(result)
    assert result["runtime_kg_route_projection_behaviour_recorded"] is True
    assert result["diagnostic_route_projection_integrated"] is True
    assert result["study_plan_route_focus_integrated"] is True
    assert result["runtime_kg_enabled_by_default"] is False
    assert result["prd3_implementation_authorised"] is False
    assert result["next_authorised_item"] == "PRD-2.7-2.9"
    # Register advanced to EXECUTION-8 after evidence capture; accept both closed states
    assert result["production_register_next_authorised_item"] in {"PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7", "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8"}
