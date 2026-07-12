from tests.support.governance_state import assert_archival_or_current_valid, assert_current_execution_state
from scripts.production_readiness.audit_prd1103r_coverage_alignment_documentation_defined_closure import audit


def test_prd1103r_authority_state_is_valid_before_capture():
    result = audit()
    assert_archival_or_current_valid(result)
    assert_archival_or_current_valid(result)
    assert result["coverage_contract_valid"] is True
    assert result["coverage_alignment_authority_recorded"] is True
    assert result["coverage_alignment_evidence_recorded"] is True
    assert_current_execution_state(result)


def test_prd1103r_preserves_release_boundaries_and_blocks_presence_only_evidence():
    result = audit()
    assert result["false_boundaries_locked"] is True
    assert result["presence_only_coverage_evidence_forbidden"] is True
    assert result["negative_path_coverage_required"] is True
