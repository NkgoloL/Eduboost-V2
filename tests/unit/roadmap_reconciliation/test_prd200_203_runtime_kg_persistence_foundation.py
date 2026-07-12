from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid
from scripts.production_readiness.audit_prd200_203_runtime_kg_persistence_foundation import audit


def test_prd200_203_authority_is_valid_before_capture() -> None:
    result = audit()
    assert_archival_or_current_valid(result)
    assert result["prd_id"] == "PRD-2.0-2.3"
    assert result["runtime_kg_enabled_by_default"] is False
    assert result["production_release_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False
    assert result["prd3_implementation_authorised"] is False
