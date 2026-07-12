from __future__ import annotations

from pathlib import Path

from scripts.production_readiness.audit_prd004_test_dependency_bootstrap_baseline import build_baseline
from scripts.roadmap_reconciliation.verify_prd004_test_dependency_bootstrap_baseline import evaluate

ROOT = Path(__file__).resolve().parents[3]


def test_prd004_authority_valid_in_current_repo_state() -> None:
    result = evaluate(ROOT)
    assert result["authority_valid"] is True
    assert result["prd003_documentation_housekeeping_ratchet_refresh_valid"] is True
    if result["test_dependency_bootstrap_baseline_recorded"]:
        assert result["valid"] is True
    else:
        assert result["valid"] is True


def test_prd004_build_baseline_records_dependency_markers() -> None:
    baseline = build_baseline(ROOT, captured_at="2026-07-07T00:00:00+00:00")
    assert baseline["schema_version"] == "prd-test-dependency-bootstrap/v1"
    assert baseline["python_backend"]["dependency_markers"]["pytest_declared"] is True
    assert baseline["python_backend"]["dependency_markers"]["pytest_cov_declared"] is True
    assert baseline["frontend"]["dependency_markers"]["vitest_declared"] is True
    assert baseline["bootstrap_contracts"]["backend_test_command"] == "PYTHONPATH=. python3 -m pytest ..."
    assert baseline["deferred_to_later_prd0_slices"]["test_failure_collection_stabilisation"] == "PRD-0.5"


def test_prd004_verifier_reports_dependency_shape() -> None:
    result = evaluate(ROOT)
    assert result["authority_valid"] is True
    assert result["requirements_file_count"] >= 5
    assert result["pytest_declared"] is True
    assert result["pytest_cov_declared"] is True
    assert result["frontend_vitest_declared"] is True
    assert result["workflow_count"] > 0


def test_prd004_boundaries_remain_closed() -> None:
    result = evaluate(ROOT)
    assert result["runtime_kg_implementation_claimed"] is True
    assert result["runtime_kg_authority_switch_authorised"] is True
    assert result["authority_switch_executed"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["prd1_implementation_authorised"] is False
