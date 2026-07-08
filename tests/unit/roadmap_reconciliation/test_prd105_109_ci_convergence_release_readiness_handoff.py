from __future__ import annotations

import json
from pathlib import Path

from scripts.production_readiness.apply_prd105_109_ci_convergence_release_readiness_handoff import apply
from scripts.roadmap_reconciliation.verify_prd105_109_ci_convergence_release_readiness_handoff import evaluate


def test_prd105_109_authority_valid_after_apply() -> None:
    apply(Path("."), write_files=True)
    result = evaluate(Path("."))
    assert result["authority_valid"] is True
    assert result["prd100_ci_release_gate_stream_authority_valid"] is True
    assert result["prd101_ci_inventory_authority_valid"] is True
    assert result["prd102_104_required_checks_workflow_release_gate_valid"] is True
    assert result["python_m_pytest_workflow_count"] == 0
    assert result["openapi_root_and_docs_match"] is True
    assert result["valid"] is False


def test_prd105_109_config_records_merged_final_scope() -> None:
    apply(Path("."), write_files=True)
    data = json.loads(Path("docs/roadmap/production_readiness/prd1_ci_convergence_release_readiness_handoff.json").read_text())
    assert data["merged_prd_slices"] == ["PRD-1.5", "PRD-1.6", "PRD-1.7", "PRD-1.8", "PRD-1.9"]
    assert data["ci_convergence_evidence"]["python_m_pytest_workflow_count"] == 0
    assert data["release_readiness_register"]["release_gate_mechanics_ready"] is True
    assert data["release_readiness_register"]["production_release_authorised"] is False
    assert data["handoff_to_prd2"]["prd2_implementation_authorised"] is False


def test_prd105_109_preserves_release_and_prd2_boundaries() -> None:
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
    assert result["required_checks_enforced"] is False
    assert result["release_gate_enforced"] is False
    assert result["branch_protection_modified"] is False
