from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from pathlib import Path

from scripts.production_readiness.audit_prd305_309_learner_parent_vertical_journey_hardening_handoff import ROOT, audit


def test_prd305_309_authority_and_recorded_states_are_valid_when_expected():
    result = audit(Path(ROOT))

    assert_archival_or_current_valid(result)
    assert result["vertical_journey_hardening_helper_valid"] is True
    assert result["live_learner_traffic_authorised"] is False
    assert result["prd4_implementation_authorised"] is False

    assert result["vertical_journey_final_hardening_recorded"] is True
    assert result["vertical_journey_final_evidence_recorded"] is True
    assert result["prd3_sequence_complete"] is True
    assert_historical_next_with_current_execution(result, "PRD-4")
