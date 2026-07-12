
from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid
from pathlib import Path

import pytest

from scripts.production_readiness.audit_prd100_ci_release_gate_stream_authority import authority_snapshot
from scripts.roadmap_reconciliation.verify_prd100_ci_release_gate_stream_authority import evaluate

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def prd100_result() -> dict:
    return evaluate(ROOT)


def test_prd100_authority_valid_after_apply(prd100_result: dict) -> None:
    assert_archival_or_current_valid(prd100_result)
    assert prd100_result["prd1_register_created"] is True
    assert prd100_result["prd1_sequence_registered"] is True


def test_prd100_keeps_release_live_and_prd2_boundaries_closed(prd100_result: dict) -> None:
    assert prd100_result["production_release_authorised"] is False
    assert prd100_result["deployment_authorised"] is False
    assert prd100_result["release_tag_authorised"] is False
    assert prd100_result["public_beta_authorised"] is False
    assert prd100_result["live_learner_traffic_authorised"] is False
    assert prd100_result["billing_launch_authorised"] is False
    assert prd100_result["live_payment_processing_authorised"] is False
    assert prd100_result["new_kg_slice_authorised"] is False
    assert prd100_result["prd2_implementation_authorised"] is False


def test_prd100_does_not_perform_ci_or_release_gate_changes(prd100_result: dict) -> None:
    assert prd100_result["no_ci_workflow_changes_performed"] is True
    assert prd100_result["no_required_check_enforcement_performed"] is True
    assert prd100_result["no_release_gate_enforcement_performed"] is True
    assert prd100_result["no_branch_protection_change_performed"] is True
    assert prd100_result["no_openapi_reconciliation_performed"] is True
    assert prd100_result["no_prd2_implementation_performed"] is True


def test_prd100_snapshot_records_prd1_sequence() -> None:
    snapshot = authority_snapshot(ROOT)
    assert snapshot["schema_version"] == "prd1-ci-release-gate-stream-authority/v1"
    assert snapshot["prd_id"] == "PRD-1.0"
    assert snapshot["stream_id"] == "PRD-1-CI-RELEASE-GATE-CONVERGENCE"
    assert snapshot["prd1_register_summary"]["prd1_sequence_registered"] is True


def test_prd100_handoff_target_is_prd1_0_or_prd1_1(prd100_result: dict) -> None:
    assert prd100_result["next_authorised_item"] in {"PRD-1.0", "PRD-1.1"}
    if prd100_result["valid"]:
        assert prd100_result["next_authorised_item"] == "PRD-1.1"
        assert str(prd100_result["register_next_authorised_item"]).startswith("PRD-1.")
