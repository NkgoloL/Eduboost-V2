from __future__ import annotations

from pathlib import Path

from scripts.production_readiness.apply_prd007_openapi_generated_artifact_canonicalisation import canonicalise
from scripts.production_readiness.audit_prd007_openapi_generated_artifact_canonicalisation import generated_artifact_inventory
from scripts.roadmap_reconciliation.verify_prd007_openapi_generated_artifact_canonicalisation import evaluate

ROOT = Path(__file__).resolve().parents[3]


def test_prd007_authority_valid_in_current_repo_state() -> None:
    result = evaluate(ROOT)
    assert result["authority_valid"] is True
    assert result["prd006_workflow_command_hygiene_ci_inventory_valid"] is True
    if result["openapi_generated_artifact_canonicalisation_recorded"]:
        assert result["valid"] is True
    else:
        assert result["valid"] is True


def test_prd007_canonicalise_reports_openapi_counts() -> None:
    result = canonicalise(ROOT, write=False)
    assert result["canonical_openapi_path"] == "docs/openapi.json"
    assert result["root_openapi_json_path"] == "openapi.json"
    assert result["root_openapi_yaml_path"] == "openapi.yaml"
    assert result["openapi_path_count"] > 0
    assert result["openapi_operation_count"] > 0


def test_prd007_generated_artifact_inventory_records_mirrors() -> None:
    inventory = generated_artifact_inventory(ROOT, captured_at="2026-07-07T00:00:00+00:00")
    assert inventory["schema_version"] == "prd-openapi-generated-artifact-canonicalisation/v1"
    assert inventory["canonical_openapi_path"] == "docs/openapi.json"
    assert inventory["root_openapi_json_path"] == "openapi.json"
    assert inventory["root_openapi_yaml_path"] == "openapi.yaml"
    assert inventory["canonical_openapi_present"] is True
    assert inventory["root_openapi_json_present"] is True
    assert inventory["root_openapi_yaml_present"] is True
    assert inventory["openapi_path_count"] > 0
    assert inventory["openapi_operation_count"] > 0


def test_prd007_boundaries_remain_closed() -> None:
    result = evaluate(ROOT)
    assert result["runtime_kg_implementation_claimed"] is True
    assert result["runtime_kg_authority_switch_authorised"] is True
    assert result["authority_switch_executed"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["prd1_implementation_authorised"] is False
