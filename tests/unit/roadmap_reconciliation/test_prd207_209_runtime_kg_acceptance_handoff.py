from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from pathlib import Path

from scripts.production_readiness.audit_prd207_209_runtime_kg_acceptance_handoff import ROOT, audit


def test_prd207_209_authority_and_final_states_are_valid_when_expected():
    result = audit(Path(ROOT))

    assert_archival_or_current_valid(result)
    assert result["runtime_kg_acceptance_report_valid"] is True
    assert result["runtime_kg_enabled_by_default"] is False
    assert result["prd3_implementation_authorised"] is False

    assert result["runtime_kg_acceptance_recorded"] is True
    assert result["runtime_kg_final_evidence_recorded"] is True
    assert result["prd2_sequence_complete"] is True
    assert_historical_next_with_current_execution(result, "PRD-3")
