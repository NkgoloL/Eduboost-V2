from pathlib import Path

from scripts.production_readiness.audit_prd207_209_runtime_kg_acceptance_handoff import ROOT, audit


def test_prd207_209_authority_and_final_states_are_valid_when_expected():
    result = audit(Path(ROOT))

    assert result["authority_valid"] is True
    assert result["runtime_kg_acceptance_report_valid"] is True
    assert result["runtime_kg_enabled_by_default"] is False
    assert result["prd3_implementation_authorised"] is False

    if result["valid"] is True:
        assert result["runtime_kg_acceptance_recorded"] is True
        assert result["runtime_kg_final_evidence_recorded"] is True
        assert result["prd2_sequence_complete"] is True
        assert result["register_next_authorised_item"] == "PRD-3"
    else:
        assert result["runtime_kg_acceptance_recorded"] is False
        assert result["next_authorised_item"] == "PRD-2.7-2.9"
        assert result["register_next_authorised_item"] == "PRD-2.7-2.9"
