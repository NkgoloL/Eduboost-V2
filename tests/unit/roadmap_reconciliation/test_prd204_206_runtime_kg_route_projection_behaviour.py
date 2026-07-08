from scripts.production_readiness.audit_prd204_206_runtime_kg_route_projection_behaviour import audit


def test_prd204_206_authority_is_valid_before_capture():
    result = audit()
    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["diagnostic_route_projection_integrated"] is True
    assert result["study_plan_route_focus_integrated"] is True
    assert result["runtime_kg_enabled_by_default"] is False
    assert result["prd3_implementation_authorised"] is False
