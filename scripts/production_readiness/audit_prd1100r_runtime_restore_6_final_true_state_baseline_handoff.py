"""Audit PRD-11.0R.RUNTIME-RESTORE-6 final true-state baseline handoff."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.runtime.final_true_state_baseline import (
    NEXT_IF_GREEN,
    NEXT_IF_RED,
    ROOT,
    evaluate_final_true_state_handoff_contract,
)

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE-6"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_6_final_true_state_baseline_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_6_final_true_state_baseline_handoff.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-6-final-true-state-baseline-handoff"
REQUIRED_PATHS = [
    "scripts/runtime/final_true_state_baseline.py",
    "scripts/runtime/verify_final_true_state_baseline.py",
    "scripts/production_readiness/audit_prd1100r_runtime_restore_6_final_true_state_baseline_handoff.py",
    "scripts/roadmap_reconciliation/verify_prd1100r_runtime_restore_6_final_true_state_baseline_handoff.py",
    "scripts/roadmap_reconciliation/capture_prd1100r_runtime_restore_6_final_true_state_baseline_handoff_evidence.py",
    "docs/testing/final_true_state_baseline_handoff_contract.md",
    "docs/engineering/prd11_runtime_restore_6_final_true_state_baseline_handoff.md",
    "docs/roadmap/production_readiness/final_true_state_baseline_handoff_contract.json",
    "docs/roadmap/production_readiness/prd_1100r_runtime_restore_6_final_true_state_baseline_handoff_record.json",
    "tests/unit/runtime/test_final_true_state_baseline.py",
    "tests/unit/roadmap_reconciliation/test_prd1100r_runtime_restore_6_final_true_state_baseline_handoff.py",
]
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
ALLOWED_NEXT = {PRD_ID, NEXT_IF_RED, NEXT_IF_GREEN, "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-1", "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_restore5_valid(root: Path) -> bool:
    record = _load(root / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_5_coverage_frontend_advisory_gate_repair_record.json")
    summary = root / "docs/roadmap/production_readiness/prd11_runtime_restore_5_coverage_frontend_advisory_gate_repair.json"
    evidence = root / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-5-coverage-frontend-advisory-gate-repair/summary.json"
    return all([
        record.get("coverage_frontend_advisory_gate_evidence_recorded") is True,
        record.get("next_authorised_item") in {PRD_ID, "PRD-11.0R.RUNTIME-RESTORE-6", NEXT_IF_RED, NEXT_IF_GREEN},
        summary.exists(),
        evidence.exists(),
    ])


def _false_boundaries_preserved(record: dict[str, Any], prod_boundaries: dict[str, Any]) -> bool:
    return all(record.get(key) is False for key in FALSE_BOUNDARIES) and all(prod_boundaries.get(key) is False for key in FALSE_BOUNDARIES)


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load(root / RECORD.relative_to(ROOT))
    register = _load(root / REGISTER.relative_to(ROOT))
    prod = _load(root / PROD_REGISTER.relative_to(ROOT))
    prod_boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    contract = evaluate_final_true_state_handoff_contract(root)
    register_next = register.get("next_authorised_item")
    prod_next = prod.get("next_authorised_item")
    boundary_valid = _false_boundaries_preserved(record, prod_boundaries)
    authority_valid = all([
        not missing_paths,
        _previous_restore5_valid(root),
        contract.get("valid") is True,
        record.get("final_true_state_baseline_handoff_authority_recorded") is True,
        record.get("final_true_state_baseline_contract_recorded") is True,
        record.get("runtime_baseline_required_green_for_handoff") is True,
        record.get("product_gate_required_green_for_handoff") is True,
        record.get("coverage_gate_required_green_for_handoff") is True,
        record.get("frontend_quality_required_green_for_handoff") is True,
        record.get("advisory_static_required_green_for_handoff") is True,
        record.get("dependency_security_required_green_for_handoff") is True,
        record.get("generated_contracts_required_green_for_handoff") is True,
        record.get("secret_baseline_required_green_for_handoff") is True,
        record.get("independent_command_outputs_required") is True,
        record.get("positive_and_negative_outputs_required") is True,
        record.get("presence_only_handoff_evidence_forbidden") is True,
        record.get("governance_substitution_for_handoff_forbidden") is True,
        record.get("controlled_handoff_to_prd1100_1104_authorised") is False,
        record.get("runtime_baseline_green") is False,
        record.get("controlled_beta_activation_operational_hold") is True,
        record.get("live_learner_traffic_operationally_safe") is False,
        record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        boundary_valid,
        register_next in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
        register_next == prod_next,
    ])
    evidence_recorded = record.get("final_true_state_baseline_handoff_evidence_recorded") is True
    record_next = record.get("next_authorised_item")
    evidence_valid = all([
        evidence_recorded,
        (root / SUMMARY.relative_to(ROOT)).exists(),
        (EVIDENCE_DIR / "summary.json").exists(),
        isinstance(record.get("final_true_state_baseline_snapshot"), dict),
        record_next in {NEXT_IF_RED, NEXT_IF_GREEN},
        register_next in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
        register_next == prod_next,
        record.get("controlled_handoff_to_prd1100_1104_authorised") == (record_next == NEXT_IF_GREEN),
    ])
    valid = authority_valid and evidence_valid
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "missing_paths": missing_paths,
        "previous_runtime_restore_5_valid": _previous_restore5_valid(root),
        "final_true_state_baseline_contract_valid": contract.get("valid") is True,
        "final_true_state_baseline_handoff_authority_recorded": record.get("final_true_state_baseline_handoff_authority_recorded") is True,
        "final_true_state_baseline_handoff_evidence_recorded": evidence_recorded,
        "runtime_baseline_required_green_for_handoff": record.get("runtime_baseline_required_green_for_handoff") is True,
        "product_gate_required_green_for_handoff": record.get("product_gate_required_green_for_handoff") is True,
        "coverage_gate_required_green_for_handoff": record.get("coverage_gate_required_green_for_handoff") is True,
        "frontend_quality_required_green_for_handoff": record.get("frontend_quality_required_green_for_handoff") is True,
        "advisory_static_required_green_for_handoff": record.get("advisory_static_required_green_for_handoff") is True,
        "independent_command_outputs_required": record.get("independent_command_outputs_required") is True,
        "presence_only_handoff_evidence_forbidden": record.get("presence_only_handoff_evidence_forbidden") is True,
        "runtime_baseline_green": record.get("runtime_baseline_green") is True,
        "product_gate_green": record.get("product_gate_green") is True,
        "coverage_gate_green": record.get("coverage_gate_green") is True,
        "frontend_quality_green": record.get("frontend_quality_green") is True,
        "advisory_static_gate_green": record.get("advisory_static_gate_green") is True,
        "all_release_gates_green": record.get("all_release_gates_green") is True,
        "controlled_handoff_to_prd1100_1104_authorised": record.get("controlled_handoff_to_prd1100_1104_authorised") is True,
        "controlled_beta_activation_operational_hold": record.get("controlled_beta_activation_operational_hold") is True,
        "live_learner_traffic_operationally_safe": record.get("live_learner_traffic_operationally_safe") is True,
        "production_release_evidence_blocked_until_runtime_baseline_green": record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        "false_boundaries_locked": boundary_valid,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register_next,
        "production_register_next_authorised_item": prod_next,
        "next_if_green": NEXT_IF_GREEN,
        "next_if_red": NEXT_IF_RED,
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
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    raise SystemExit(0 if (result.get("authority_valid") if args.authority_only else result.get("valid")) else 1)
