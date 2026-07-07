from __future__ import annotations

import json
from pathlib import Path

from scripts.roadmap_reconciliation.verify_prd003_documentation_housekeeping_ratchet_refresh import evaluate

ROOT = Path(__file__).resolve().parents[3]


def test_prd003_authority_is_valid() -> None:
    result = evaluate(ROOT)
    assert result["authority_valid"] is True, result["errors"]
    assert result["prd_id"] == "PRD-0.3"
    assert result["prd002_historical_report_stale_source_quarantine_valid"] is True


def test_prd003_boundaries_are_preserved() -> None:
    result = evaluate(ROOT)
    assert result["runtime_kg_implementation_claimed"] is True
    assert result["runtime_kg_authority_switch_authorised"] is True
    assert result["authority_switch_executed"] is True
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False
    assert result["new_kg_slice_authorised"] is False
    assert result["prd1_implementation_authorised"] is False


def test_documentation_inventory_and_ratchet_baseline_exist() -> None:
    inventory = json.loads((ROOT / "docs/generated/documentation_inventory.json").read_text(encoding="utf-8"))
    baseline = json.loads((ROOT / "docs/documentation/housekeeping_ratchet_baseline.json").read_text(encoding="utf-8"))
    assert inventory["summary"]["schema_version"] == "doc-inventory/v2-deterministic-lfs-aware"
    assert inventory["summary"]["markdown_files"] > 0
    assert "documents" in inventory
    assert "findings" in inventory
    assert baseline["schema_version"] == "doc-housekeeping-ratchet/v1"
    assert baseline["baseline_source"] == "docs/generated/documentation_inventory.json"
    assert baseline["strict_zero_new_finding_types"] is True


def test_prd003_plan_states_refresh_without_debt_elimination_claim() -> None:
    plan = (ROOT / "docs/roadmap/production_readiness/documentation_housekeeping_ratchet_refresh_plan.md").read_text(encoding="utf-8")
    assert "Regenerate deterministic documentation inventory outputs" in plan
    assert "Refresh the housekeeping ratchet baseline" in plan
    assert "does not claim that documentation debt is eliminated" in plan
