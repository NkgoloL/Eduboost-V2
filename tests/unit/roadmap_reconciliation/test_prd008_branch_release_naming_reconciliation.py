from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid
from pathlib import Path

from scripts.production_readiness.apply_prd008_branch_release_naming_reconciliation import apply as apply_reconciliation
from scripts.production_readiness.audit_prd008_branch_release_naming_reconciliation import branch_release_inventory
from scripts.roadmap_reconciliation.verify_prd008_branch_release_naming_reconciliation import evaluate

ROOT = Path(__file__).resolve().parents[3]


def test_prd008_authority_valid_in_current_repo_state() -> None:
    result = evaluate(ROOT)
    assert_archival_or_current_valid(result)
    assert result["branch_release_naming_reconciliation_recorded"] is True
    if result["branch_release_naming_reconciliation_recorded"]:
        assert_archival_or_current_valid(result)
    else:
        assert_archival_or_current_valid(result)


def test_prd008_inventory_records_branch_and_release_counts() -> None:
    inventory = branch_release_inventory(ROOT, captured_at="2026-07-08T00:00:00+00:00")
    assert inventory["schema_version"] == "prd-branch-release-naming-reconciliation/v1"
    assert inventory["canonical_trunk_branch"] == "master"
    assert inventory["release_branch_pattern"] == "release/**"
    assert inventory["workflow_count"] > 0
    assert inventory["workflow_branch_reference_summary"]["master_workflow_count"] > 0


def test_prd008_apply_reconciles_branching_policy_doc() -> None:
    result = apply_reconciliation(ROOT, write=False)
    assert result["canonical_trunk_branch"] == "master"
    assert result["legacy_main_alias_policy"] == "compatibility-only"
    assert result["release_branch_pattern"] == "release/**"
    inventory = branch_release_inventory(ROOT)
    assert inventory["branching_policy_document_refreshed"] is True
    assert inventory["stale_main_trunk_claim_present"] is False


def test_prd008_boundaries_remain_closed() -> None:
    result = evaluate(ROOT)
    assert result["runtime_kg_implementation_claimed"] is True
    assert result["runtime_kg_authority_switch_authorised"] is True
    assert result["authority_switch_executed"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["release_tag_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["prd1_implementation_authorised"] is False
