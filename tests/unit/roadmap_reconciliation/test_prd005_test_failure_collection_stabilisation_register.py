from __future__ import annotations

from pathlib import Path

from scripts.production_readiness.audit_prd005_test_failure_collection_stabilisation_register import build_stabilisation_register
from scripts.roadmap_reconciliation.verify_prd005_test_failure_collection_stabilisation_register import evaluate

ROOT = Path(__file__).resolve().parents[3]


def test_prd005_authority_valid_in_current_repo_state() -> None:
    result = evaluate(ROOT)
    assert result["authority_valid"] is True
    assert result["prd004_test_dependency_bootstrap_baseline_valid"] is True
    if result["test_failure_collection_stabilisation_register_recorded"]:
        assert result["valid"] is True
    else:
        assert result["valid"] is True


def test_prd005_build_register_records_test_inventory() -> None:
    baseline = build_stabilisation_register(ROOT, captured_at="2026-07-07T00:00:00+00:00")
    assert baseline["schema_version"] == "prd-test-failure-collection-stabilisation/v1"
    assert baseline["test_inventory"]["test_file_count"] > 0
    assert baseline["test_inventory"]["test_function_count"] > 0
    assert len(baseline["collection_command_matrix"]) >= 5
    assert baseline["stabilisation_boundaries"]["no_test_deletions_authorised"] is True


def test_prd005_classification_schema_and_triage_register() -> None:
    baseline = build_stabilisation_register(ROOT, captured_at="2026-07-07T00:00:00+00:00")
    categories = {item["category"] for item in baseline["failure_classification_schema"]}
    assert "dependency_bootstrap" in categories
    assert "import_or_collection" in categories
    assert "stale_test_contract" in categories
    assert "frontend_tooling" in categories
    assert len(baseline["triage_register"]) >= 5
    assert all(item["delete_tests_authorised"] is False for item in baseline["triage_register"])


def test_prd005_boundaries_remain_closed() -> None:
    result = evaluate(ROOT)
    assert result["runtime_kg_implementation_claimed"] is True
    assert result["runtime_kg_authority_switch_authorised"] is True
    assert result["authority_switch_executed"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["prd1_implementation_authorised"] is False
