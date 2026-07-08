from scripts.production_readiness.audit_prd204_206_runtime_kg_route_projection_behaviour import audit


def test_prd204_206_evidence_is_fully_recorded():
    result = audit()
    assert result["authority_valid"] is True
    assert result["valid"] is True
    assert result["runtime_kg_route_projection_behaviour_recorded"] is True
    assert result["diagnostic_route_projection_integrated"] is True
    assert result["study_plan_route_focus_integrated"] is True
    assert result["runtime_kg_enabled_by_default"] is False
    assert result["prd3_implementation_authorised"] is False
    assert result["register_next_authorised_item"] == "PRD-2.7-2.9"
