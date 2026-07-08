from __future__ import annotations

from pathlib import Path

import pytest

from scripts.production_readiness.audit_prd101_ci_inventory_authority import collect_ci_inventory, inventory_snapshot
from scripts.roadmap_reconciliation.verify_prd101_ci_inventory_authority import evaluate

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def prd101_result() -> dict:
    return evaluate(ROOT)


def test_prd101_authority_valid_after_apply(prd101_result: dict) -> None:
    assert prd101_result["authority_valid"] is True
    assert prd101_result["prd100_ci_release_gate_stream_authority_valid"] is True
    assert prd101_result["workflow_count"] > 0


def test_prd101_inventory_collects_core_dimensions() -> None:
    inventory = collect_ci_inventory(ROOT)
    assert inventory["schema_version"] == "prd1-ci-inventory-authority/v1"
    assert inventory["prd_id"] == "PRD-1.1"
    assert inventory["summary"]["workflow_count"] > 0
    assert "makefile_inventory" in inventory
    assert "openapi_inventory" in inventory
    assert "branch_protection_inventory" in inventory


def test_prd101_keeps_classification_canonicalisation_and_release_gates_closed(prd101_result: dict) -> None:
    assert prd101_result["no_required_check_classification_performed"] is True
    assert prd101_result["no_workflow_canonicalisation_performed"] is True
    assert prd101_result["no_ci_workflow_changes_performed"] is True
    assert prd101_result["no_required_check_enforcement_performed"] is True
    assert prd101_result["no_release_gate_enforcement_performed"] is True
    assert prd101_result["no_branch_protection_change_performed"] is True
    assert prd101_result["no_openapi_reconciliation_performed"] is True
    assert prd101_result["no_prd2_implementation_performed"] is True


def test_prd101_keeps_release_live_and_prd2_boundaries_closed(prd101_result: dict) -> None:
    assert prd101_result["production_release_authorised"] is False
    assert prd101_result["deployment_authorised"] is False
    assert prd101_result["release_tag_authorised"] is False
    assert prd101_result["public_beta_authorised"] is False
    assert prd101_result["live_learner_traffic_authorised"] is False
    assert prd101_result["billing_launch_authorised"] is False
    assert prd101_result["live_payment_processing_authorised"] is False
    assert prd101_result["new_kg_slice_authorised"] is False
    assert prd101_result["prd2_implementation_authorised"] is False


def test_prd101_snapshot_records_inventory_summary() -> None:
    snapshot = inventory_snapshot(ROOT)
    assert snapshot["schema_version"] == "prd1-ci-inventory-authority/v1"
    assert snapshot["summary"]["workflow_count"] > 0
    assert snapshot["next_authorised_item"] == "PRD-1.2"


def test_prd101_handoff_target_is_prd1_1_or_prd1_2(prd101_result: dict) -> None:
    assert prd101_result["next_authorised_item"] in {"PRD-1.1", "PRD-1.2", "PRD-1.5", "PRD-2"}
    if prd101_result["valid"]:
        assert prd101_result["next_authorised_item"] == "PRD-1.2"
        assert prd101_result["register_next_authorised_item"] in {"PRD-1.2", "PRD-1.5", "PRD-2"}
