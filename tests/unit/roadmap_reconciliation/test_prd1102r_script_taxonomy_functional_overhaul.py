from scripts.production_readiness.audit_prd1102r_script_taxonomy_functional_overhaul import audit


def test_prd1102r_authority_state_is_valid() -> None:
    result = audit()
    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["taxonomy_valid"] is True
    assert result["script_taxonomy_authority_recorded"] is True
    assert result["script_taxonomy_evidence_recorded"] is False
    assert result["prd113r_handoff_authorised"] is False
    assert result["register_next_authorised_item"] == "PRD-11.2R"


def test_prd1102r_release_boundaries_are_locked() -> None:
    result = audit()
    assert result["false_boundaries_locked"] is True
    assert result["script_outputs_cannot_self_prove_release_readiness"] is True
    assert result["functional_roles_recorded"] is True
