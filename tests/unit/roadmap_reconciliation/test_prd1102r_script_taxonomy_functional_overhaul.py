from tests.support.governance_state import assert_archival_or_current_valid, assert_current_execution_state
from scripts.production_readiness.audit_prd1102r_script_taxonomy_functional_overhaul import audit


def test_prd1102r_authority_state_is_valid() -> None:
    result = audit()
    assert_archival_or_current_valid(result)
    assert_archival_or_current_valid(result)
    assert result["taxonomy_valid"] is True
    assert result["script_taxonomy_authority_recorded"] is True
    assert result["script_taxonomy_evidence_recorded"] is True
    assert result["prd113r_handoff_authorised"] is True
    assert_current_execution_state(result)


def test_prd1102r_release_boundaries_are_locked() -> None:
    result = audit()
    assert result["false_boundaries_locked"] is True
    assert result["script_outputs_cannot_self_prove_release_readiness"] is True
    assert result["functional_roles_recorded"] is True
