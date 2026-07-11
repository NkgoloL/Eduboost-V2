"""Audit PRD-11.0R true-state runtime baseline restoration gate."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.0R"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_true_state_runtime_baseline_restoration_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_true_state_runtime_baseline_restoration.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-true-state-runtime-baseline-restoration"
REQUIRED_PATHS = [
    "app/modules/production_release/true_state_baseline.py",
    "app/modules/production_release/__init__.py",
    "app/api_v2_routers/production_release.py",
    "docs/engineering/prd11_true_state_runtime_baseline_restoration.md",
    "docs/roadmap/production_readiness/prd_1100r_true_state_runtime_baseline_restoration_record.json",
    "scripts/production_readiness/collect_prd1100r_true_state_runtime_baseline.py",
    "scripts/production_readiness/audit_prd1100r_true_state_runtime_baseline_restoration.py",
    "scripts/roadmap_reconciliation/verify_prd1100r_true_state_runtime_baseline_restoration.py",
    "scripts/roadmap_reconciliation/capture_prd1100r_true_state_runtime_baseline_restoration_evidence.py",
    "tests/unit/modules/production_release/test_true_state_runtime_baseline.py",
    "tests/unit/roadmap_reconciliation/test_prd1100r_true_state_runtime_baseline_restoration.py",
]
REQUIRED_CONCERNS = {
    "runtime_readiness_probe_503",
    "database_lineage_unknown_revision",
    "orm_live_schema_drift",
    "diagnostic_items_irt_column_drift",
    "backend_unit_gate_red",
    "integration_popia_contract_failures",
    "frontend_lint_and_vitest_red",
    "openapi_route_inventory_drift",
    "dependency_security_red",
    "secret_baseline_noise",
    "coverage_baseline_untrusted",
    "deterministic_readiness_endpoints_not_runtime_proof",
    "external_approval_gates_missing",
}
FALSE_BOUNDARIES = [
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "prd12_implementation_authorised",
]
ALLOWED_NEXT = {"PRD-11.0R", "PRD-11.0R.RUNTIME-RESTORE", "PRD-11.0R.RUNTIME-RESTORE-1", "PRD-11.0R.RUNTIME-RESTORE-2", "PRD-11.0R.RUNTIME-RESTORE-3", "PRD-11.0R.RUNTIME-RESTORE-4", "PRD-11.0R.RUNTIME-RESTORE-5", "PRD-11.0R.RUNTIME-RESTORE-6", "PRD-11.0R.RUNTIME-RESTORE.EXECUTION", "PRD-11.0-11.4"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd10_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd1005_1009_controlled_beta_final_live_traffic_handoff import audit as audit_prd1005
        result = audit_prd1005(root)
        return result.get("valid") is True or all([
            result.get("controlled_beta_final_evidence_recorded") is True,
            result.get("prd10_sequence_complete") is True,
            result.get("prd11_handoff_authorised") is True,
            result.get("live_learner_traffic_authorised") is True,
        ])
    except Exception:
        return False


def _runtime_baseline_helper_valid(root: Path) -> bool:
    try:
        from app.modules.production_release import (
            build_default_true_state_runtime_baseline_report,
            build_green_true_state_runtime_baseline_report,
        )
        hold = build_default_true_state_runtime_baseline_report().to_payload()
        green = build_green_true_state_runtime_baseline_report().to_payload()
    except Exception:
        return False
    route_text = (root / "app/api_v2_routers/production_release.py").read_text() if (root / "app/api_v2_routers/production_release.py").exists() else ""
    return all([
        hold.get("prd_id") == PRD_ID,
        hold.get("accepted") is True,
        hold.get("runtime_baseline_green") is False,
        hold.get("controlled_beta_activation_operational_hold") is True,
        hold.get("live_learner_traffic_operationally_safe") is False,
        hold.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        hold.get("production_release_authorised") is False,
        hold.get("deployment_authorised") is False,
        hold.get("public_beta_authorised") is False,
        green.get("runtime_baseline_green") is True,
        green.get("controlled_beta_activation_operational_hold") is False,
        "get_true_state_runtime_baseline" in route_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load(root / RECORD.relative_to(ROOT))
    register = _load(root / REGISTER.relative_to(ROOT))
    prod = _load(root / PROD_REGISTER.relative_to(ROOT))
    summary = _load(root / SUMMARY.relative_to(ROOT))
    current_truth = prod.get("current_truth", {}) if isinstance(prod.get("current_truth"), dict) else {}
    prod_boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    concerns = set(record.get("concerns_addressed", []))
    concern_coverage_valid = REQUIRED_CONCERNS.issubset(concerns)
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    prod_false_boundaries_preserved = all(prod_boundaries.get(key) is False for key in FALSE_BOUNDARIES if key != "prd12_implementation_authorised")
    operational_hold_valid = all([
        record.get("controlled_beta_activation_operational_hold") is True,
        record.get("live_learner_traffic_operationally_safe") is False,
        record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        record.get("baseline_green_required_before_prd1100_evidence_capture") is True,
        record.get("runtime_evidence_mode") == "actual_probe_evidence_required_not_constant_status",
    ])
    authority_valid = all([
        not missing_paths,
        _previous_prd10_valid(root),
        _runtime_baseline_helper_valid(root),
        record.get("true_state_runtime_baseline_restoration_authority_recorded") is True,
        record.get("true_state_report_reconciled") is True,
        record.get("operational_hold_recorded") is True,
        concern_coverage_valid,
        operational_hold_valid,
        false_boundaries_preserved,
        prod_false_boundaries_preserved,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod.get("next_authorised_item") in ALLOWED_NEXT,
    ])
    evidence_recorded = record.get("true_state_runtime_baseline_evidence_recorded") is True
    baseline = record.get("true_state_runtime_baseline_snapshot") if isinstance(record.get("true_state_runtime_baseline_snapshot"), dict) else {}
    baseline_evidence_valid = all([
        evidence_recorded,
        baseline.get("prd_id") == PRD_ID,
        baseline.get("release_evidence_mode") == "actual_probe_evidence_required_not_constant_status",
        isinstance(baseline.get("checks"), dict),
        bool(baseline.get("hard_gate_names")),
        record.get("controlled_beta_activation_operational_hold") is True,
        current_truth.get("controlled_beta_activation_operational_hold") is True,
        current_truth.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
    ])
    valid = all([
        authority_valid,
        baseline_evidence_valid,
        record.get("next_authorised_item") == "PRD-11.0R.RUNTIME-RESTORE",
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod.get("next_authorised_item") in ALLOWED_NEXT,
        register.get("next_authorised_item") == prod.get("next_authorised_item"),
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "missing_paths": missing_paths,
        "previous_prd10_handoff_valid": _previous_prd10_valid(root),
        "runtime_baseline_helper_valid": _runtime_baseline_helper_valid(root),
        "true_state_runtime_baseline_restoration_authority_recorded": record.get("true_state_runtime_baseline_restoration_authority_recorded") is True,
        "true_state_runtime_baseline_evidence_recorded": evidence_recorded,
        "true_state_report_reconciled": record.get("true_state_report_reconciled") is True,
        "concern_coverage_valid": concern_coverage_valid,
        "operational_hold_recorded": record.get("operational_hold_recorded") is True,
        "controlled_beta_activation_operational_hold": record.get("controlled_beta_activation_operational_hold") is True,
        "controlled_beta_live_traffic_authorised": record.get("controlled_beta_live_traffic_authorised") is True,
        "live_learner_traffic_authorised": record.get("live_learner_traffic_authorised") is True,
        "live_learner_traffic_operationally_safe": record.get("live_learner_traffic_operationally_safe") is True,
        "production_release_evidence_blocked_until_runtime_baseline_green": record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        "runtime_baseline_green": record.get("runtime_baseline_green") is True,
        "runtime_baseline_status": record.get("runtime_baseline_status"),
        "production_release_authorised": record.get("production_release_authorised") is True,
        "deployment_authorised": record.get("deployment_authorised") is True,
        "public_beta_authorised": record.get("public_beta_authorised") is True,
        "billing_launch_authorised": record.get("billing_launch_authorised") is True,
        "live_payment_processing_authorised": record.get("live_payment_processing_authorised") is True,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod.get("next_authorised_item"),
        "baseline_blockers": baseline.get("blockers", []),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--authority-only", action="store_true")
    args = parser.parse_args()
    result = audit(ROOT)
    if args.authority_only:
        result = {**result, "valid": False}
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"{PRD_ID}: valid={result['valid']} authority_valid={result['authority_valid']}")
    raise SystemExit(0 if (result.get("authority_valid") if args.authority_only else result.get("valid")) else 1)
