from __future__ import annotations

from tests.support.governance_state import assert_archival_or_current_valid
import json
import shutil
from pathlib import Path

from scripts.roadmap_reconciliation.verify_prd003_documentation_housekeeping_ratchet_refresh import evaluate

ROOT = Path(__file__).resolve().parents[3]


def _prd003_fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "docs", root / "docs")
    shutil.copytree(ROOT / "scripts/maintenance", root / "scripts/maintenance")
    shutil.copy2(ROOT / "README.md", root / "README.md")

    generated = root / "docs/generated"
    generated.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((ROOT / "tests/fixtures/documentation_inventory.json").read_text(encoding="utf-8"))
    (generated / "documentation_inventory.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (generated / "documentation_inventory.csv").write_text(
        "path,title\n"
        "docs/current_state.md,Current State\n",
        encoding="utf-8",
    )
    (generated / "documentation_findings.csv").write_text(
        "path,finding_type,message\n",
        encoding="utf-8",
    )

    baseline_path = root / "docs/documentation/housekeeping_ratchet_baseline.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline["note"] = "PRD-0.3 fixture baseline captured for archival authority validation."
    baseline_path.write_text(json.dumps(baseline, indent=2, sort_keys=True), encoding="utf-8")
    return root


def test_prd003_authority_is_valid(tmp_path: Path) -> None:
    result = evaluate(_prd003_fixture_root(tmp_path))
    assert_archival_or_current_valid(result)
    assert result["prd_id"] == "PRD-0.3"
    assert result["documentation_housekeeping_ratchet_refresh_recorded"] is True
    assert result["documentation_inventory_schema_valid"] is True


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
    inventory_path = ROOT / "docs/generated/documentation_inventory.json"
    if not inventory_path.exists():
        inventory_path = ROOT / "tests/fixtures/documentation_inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
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
