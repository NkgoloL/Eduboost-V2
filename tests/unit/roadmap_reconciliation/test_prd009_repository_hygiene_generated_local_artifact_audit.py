from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid
from pathlib import Path

from scripts.production_readiness.apply_prd009_repository_hygiene_generated_local_artifact_audit import apply as apply_hygiene_policy
from scripts.production_readiness.audit_prd009_repository_hygiene_generated_local_artifact_audit import repository_hygiene_inventory
from scripts.roadmap_reconciliation.verify_prd009_repository_hygiene_generated_local_artifact_audit import evaluate

ROOT = Path(__file__).resolve().parents[3]


def test_prd009_authority_valid_after_apply() -> None:
    result = evaluate(ROOT)
    assert_archival_or_current_valid(result)
    assert result["repository_hygiene_generated_local_artifact_audit_recorded"] is True
    assert result["repository_hygiene_policy_document_refreshed"] is True
    assert result["generated_local_cleanup_authorised"] is False
    assert result["file_deletion_authorised"] is False
    assert result["repository_history_rewrite_authorised"] is False
    assert result["prd1_implementation_authorised"] is False


def test_prd009_inventory_records_generated_local_candidates() -> None:
    inventory = repository_hygiene_inventory(ROOT)
    assert inventory["schema_version"] == "prd-repository-hygiene-generated-local-artifact-audit/v1"
    assert inventory["prd_id"] == "PRD-0.9"
    assert inventory["summary"]["configured_generated_local_path_count"] >= 20
    paths = {item["path"] for item in inventory["generated_local_artifact_candidates"]}
    assert "coverage.xml" in paths
    assert "logs" in paths
    assert "temp" in paths
    assert "eduboost.egg-info" in paths


def test_prd009_inventory_records_suspicious_top_level_candidates() -> None:
    inventory = repository_hygiene_inventory(ROOT)
    suspicious_paths = {item["path"] for item in inventory["suspicious_top_level_entries"]}
    assert "cripts" in suspicious_paths
    assert "tatus" in suspicious_paths
    assert "ubprocess, sys" in suspicious_paths
    assert any(path.startswith("coped technical delivery directories") for path in suspicious_paths)


def test_prd009_apply_refreshes_policy_without_cleanup_authority() -> None:
    result = apply_hygiene_policy(ROOT, write=False)
    assert result["repository_hygiene_policy_document_refreshed"] is True
    assert result["generated_local_cleanup_authorised"] is False
    assert result["file_deletion_authorised"] is False
    assert result["repository_history_rewrite_authorised"] is False


def test_prd009_boundaries_remain_closed() -> None:
    result = evaluate(ROOT)
    assert result["runtime_kg_implementation_claimed"] is True
    assert result["runtime_kg_authority_switch_authorised"] is True
    assert result["authority_switch_executed"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["release_tag_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False
    assert result["new_kg_slice_authorised"] is False
    assert result["prd1_implementation_authorised"] is False
