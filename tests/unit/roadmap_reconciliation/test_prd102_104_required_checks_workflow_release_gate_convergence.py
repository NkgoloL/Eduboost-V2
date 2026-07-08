from __future__ import annotations

import json
from pathlib import Path

from scripts.production_readiness.apply_prd102_104_required_checks_workflow_release_gate_convergence import apply
from scripts.roadmap_reconciliation.verify_prd102_104_required_checks_workflow_release_gate_convergence import evaluate


def test_prd102_104_authority_valid_after_apply() -> None:
    apply(Path("."), write_files=True)
    result = evaluate(Path("."))
    assert result["authority_valid"] is True
    assert result["prd101_ci_inventory_authority_valid"] is True
    assert result["required_check_classification_performed"] is True
    assert result["workflow_canonicalisation_performed"] is True
    assert result["ci_workflow_changes_performed"] is True
    assert result["openapi_reconciliation_performed"] is True
    assert result["python_m_pytest_workflow_count"] == 0
    assert result["required_checks_enforced"] is False
    assert result["release_gate_enforced"] is False
    assert result["branch_protection_modified"] is False
    assert result["valid"] is False


def test_prd102_104_config_records_merged_scope() -> None:
    apply(Path("."), write_files=True)
    data = json.loads(Path("docs/roadmap/production_readiness/prd1_required_checks_workflow_release_gate_convergence.json").read_text())
    assert data["merged_prd_slices"] == ["PRD-1.2", "PRD-1.3", "PRD-1.4"]
    assert data["required_check_classification"]["classification_performed"] is True
    assert data["workflow_canonicalisation"]["canonical_pytest_command"] == "python3 -m pytest"
    assert data["openapi_reconciliation"]["root_and_docs_openapi_match"] is True
    assert data["release_gate_definition"]["canonical_trunk_branch"] == "master"
    assert data["release_gate_definition"]["release_gate_enforced"] is False


def test_prd102_104_preserves_prd2_and_release_boundaries() -> None:
    apply(Path("."), write_files=True)
    result = evaluate(Path("."))
    assert result["prd2_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["release_tag_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False
