from __future__ import annotations

import json
from pathlib import Path

from scripts.maintenance.check_readiness_register_consistency import evaluate


BOUNDARIES = {
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
    "public_beta_live_traffic_authorised": False,
    "live_learner_traffic_authorised": False,
    "billing_launch_authorised": False,
    "live_payment_processing_authorised": False,
    "new_kg_slice_authorised": False,
}


def _write_fixture(root: Path, *, conflicting: bool = False) -> None:
    readiness = {
        **BOUNDARIES,
        "authority_boundaries": BOUNDARIES,
        "next_authorised_item": "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8",
        "all_advisory_gates_green": False,
        "current_truth": {
            "advisory_static_gate_green": False,
            "coverage_gate_green": False,
            "dependency_audit_gate_green": False,
            "secret_baseline_gate_green": False,
            "runtime_baseline_green": True,
            "critical_product_flows_green": True,
            "frontend_quality_green": True,
            "generated_contracts_green": True,
            "prd11_next_authorised_item": "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8",
        },
    }
    prd11 = {
        **BOUNDARIES,
        "authority_boundaries": BOUNDARIES,
        "next_authorised_item": "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8",
        "all_advisory_gates_green": False,
        "current_truth": readiness["current_truth"].copy(),
    }
    if conflicting:
        readiness["coverage_gate_green"] = True
        readiness["current_truth"]["coverage_gate_green"] = False
    base = root / "docs/roadmap/production_readiness"
    base.mkdir(parents=True)
    (base / "production_readiness_register.json").write_text(json.dumps(readiness), encoding="utf-8")
    (base / "prd11_production_release_register.json").write_text(json.dumps(prd11), encoding="utf-8")
    (base / "true_state_remediation_register.json").write_text(
        json.dumps({"current_bundle": "B03", "bundles": [{"id": "B03", "status": "verified"}]}),
        encoding="utf-8",
    )
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs/current_state.md").write_text("Active implementation bundle: B03 (CI)\n", encoding="utf-8")


def test_consistency_check_passes_for_aligned_registers(tmp_path: Path) -> None:
    _write_fixture(tmp_path)

    result = evaluate(tmp_path)

    assert result["valid"] is True
    assert result["errors"] == []


def test_consistency_check_rejects_duplicate_field_conflict(tmp_path: Path) -> None:
    _write_fixture(tmp_path, conflicting=True)

    result = evaluate(tmp_path)

    assert result["valid"] is False
    assert any("coverage_gate_green" in error for error in result["errors"])
