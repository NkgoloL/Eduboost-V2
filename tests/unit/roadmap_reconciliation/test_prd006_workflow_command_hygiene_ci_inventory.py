from __future__ import annotations

from pathlib import Path

from scripts.production_readiness.apply_prd006_workflow_command_hygiene import rewrite_line
from scripts.production_readiness.audit_prd006_workflow_command_hygiene_ci_inventory import workflow_inventory
from scripts.roadmap_reconciliation.verify_prd006_workflow_command_hygiene_ci_inventory import evaluate

ROOT = Path(__file__).resolve().parents[3]


def test_prd006_authority_valid_in_current_repo_state() -> None:
    result = evaluate(ROOT)
    assert result["authority_valid"] is True
    assert result["prd005_test_failure_collection_stabilisation_register_valid"] is True
    if result["workflow_command_hygiene_ci_inventory_recorded"]:
        assert result["valid"] is True
    else:
        assert result["valid"] is False


def test_prd006_rewrite_line_converts_direct_pytest_only() -> None:
    line, changed = rewrite_line("          pytest -q tests/unit --no-cov\n")
    assert changed is True
    assert "PYTHONPATH=. python3 -m pytest -q tests/unit --no-cov" in line
    preserved, preserved_changed = rewrite_line("          python3 -m pytest -q tests/unit --no-cov\n")
    assert preserved_changed is False
    assert preserved == "          python3 -m pytest -q tests/unit --no-cov\n"
    install, install_changed = rewrite_line("          python -m pip install pytest pytest-asyncio\n")
    assert install_changed is False
    assert install == "          python -m pip install pytest pytest-asyncio\n"


def test_prd006_workflow_inventory_records_command_hygiene() -> None:
    inventory = workflow_inventory(ROOT, captured_at="2026-07-07T00:00:00+00:00")
    assert inventory["schema_version"] == "prd-workflow-command-hygiene-ci-inventory/v1"
    assert inventory["workflow_count"] > 0
    assert inventory["module_pytest_command_count"] > 0
    assert inventory["command_hygiene_policy"]["canonical_pytest_command"] == "PYTHONPATH=. python3 -m pytest"
    assert inventory["command_hygiene_policy"]["direct_pytest_invocations_allowed"] is False


def test_prd006_boundaries_remain_closed() -> None:
    result = evaluate(ROOT)
    assert result["runtime_kg_implementation_claimed"] is True
    assert result["runtime_kg_authority_switch_authorised"] is True
    assert result["authority_switch_executed"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["prd1_implementation_authorised"] is False
