"""Audit PRD-11.0R.RUNTIME-RESTORE-4 product gate execution and critical-flow repair."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.test_suites.product_gate_execution import evaluate_product_gate_execution_contract

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.0R.RUNTIME-RESTORE-4"
NEXT_AFTER_EVIDENCE = "PRD-11.0R.RUNTIME-RESTORE-5"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_4_product_gate_execution_critical_flow_repair_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_4_product_gate_execution_critical_flow_repair.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-4-product-gate-execution-critical-flow-repair"
REQUIRED_PATHS = [
    "scripts/test_suites/product_gate_execution.py",
    "scripts/test_suites/run_product_gate_execution.py",
    "scripts/test_suites/verify_product_gate_execution.py",
    "scripts/production_readiness/audit_prd1100r_runtime_restore_4_product_gate_execution_critical_flow_repair.py",
    "scripts/roadmap_reconciliation/verify_prd1100r_runtime_restore_4_product_gate_execution_critical_flow_repair.py",
    "scripts/roadmap_reconciliation/capture_prd1100r_runtime_restore_4_product_gate_execution_critical_flow_repair_evidence.py",
    "docs/testing/product_gate_execution_contract.md",
    "docs/engineering/prd11_runtime_restore_4_product_gate_execution_critical_flow_repair.md",
    "docs/roadmap/production_readiness/product_gate_execution_contract.json",
    "docs/roadmap/production_readiness/prd_1100r_runtime_restore_4_product_gate_execution_critical_flow_repair_record.json",
    "tests/unit/test_suites/test_product_gate_execution.py",
    "tests/unit/roadmap_reconciliation/test_prd1100r_runtime_restore_4_product_gate_execution_critical_flow_repair.py",
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
ALLOWED_NEXT = {PRD_ID, NEXT_AFTER_EVIDENCE, "PRD-11.0R.RUNTIME-RESTORE-6"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_restore3_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd1100r_runtime_restore_3_product_runtime_test_gate_repair import audit as audit_restore3
        result = audit_restore3(root)
        return result.get("valid") is True or all([
            result.get("product_runtime_test_gate_evidence_recorded") is True,
            result.get("register_next_authorised_item") in ALLOWED_NEXT,
            result.get("production_register_next_authorised_item") in ALLOWED_NEXT,
        ])
    except Exception:
        return False


def _false_boundaries_preserved(record: dict[str, Any], prod_boundaries: dict[str, Any]) -> bool:
    return all(record.get(key) is False for key in FALSE_BOUNDARIES) and all(prod_boundaries.get(key) is False for key in FALSE_BOUNDARIES)


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load(root / RECORD.relative_to(ROOT))
    register = _load(root / REGISTER.relative_to(ROOT))
    prod = _load(root / PROD_REGISTER.relative_to(ROOT))
    prod_boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    contract = evaluate_product_gate_execution_contract(root)
    register_next = register.get("next_authorised_item")
    prod_next = prod.get("next_authorised_item")
    boundary_valid = _false_boundaries_preserved(record, prod_boundaries)
    authority_valid = all([
        not missing_paths,
        _previous_restore3_valid(root),
        contract.get("valid") is True,
        record.get("product_gate_execution_authority_recorded") is True,
        record.get("product_gate_execution_contract_recorded") is True,
        record.get("critical_product_flows_recorded") is True,
        record.get("positive_and_negative_flow_evidence_required") is True,
        record.get("independent_command_outputs_required") is True,
        record.get("presence_only_flow_evidence_forbidden") is True,
        record.get("runtime_context_required_for_db_backed_flows") is True,
        record.get("known_failures_recorded_as_blockers") is True,
        record.get("product_gate_green") is False,
        record.get("runtime_baseline_green") is False,
        record.get("controlled_beta_activation_operational_hold") is True,
        record.get("live_learner_traffic_operationally_safe") is False,
        record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        boundary_valid,
        register_next in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
        register_next == prod_next,
    ])
    evidence_recorded = record.get("product_gate_execution_evidence_recorded") is True
    evidence_valid = all([
        evidence_recorded,
        (root / SUMMARY.relative_to(ROOT)).exists(),
        (EVIDENCE_DIR / "summary.json").exists(),
        isinstance(record.get("product_gate_execution_contract_snapshot"), dict),
        record.get("next_authorised_item") == NEXT_AFTER_EVIDENCE,
        register_next in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
    ])
    valid = authority_valid and evidence_valid
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "missing_paths": missing_paths,
        "previous_runtime_restore_3_valid": _previous_restore3_valid(root),
        "product_gate_execution_contract_valid": contract.get("valid") is True,
        "product_gate_execution_authority_recorded": record.get("product_gate_execution_authority_recorded") is True,
        "product_gate_execution_evidence_recorded": evidence_recorded,
        "critical_product_flows_recorded": record.get("critical_product_flows_recorded") is True,
        "positive_and_negative_flow_evidence_required": record.get("positive_and_negative_flow_evidence_required") is True,
        "independent_command_outputs_required": record.get("independent_command_outputs_required") is True,
        "presence_only_flow_evidence_forbidden": record.get("presence_only_flow_evidence_forbidden") is True,
        "runtime_context_required_for_db_backed_flows": record.get("runtime_context_required_for_db_backed_flows") is True,
        "known_failures_recorded_as_blockers": record.get("known_failures_recorded_as_blockers") is True,
        "runtime_baseline_green": record.get("runtime_baseline_green") is True,
        "product_gate_green": record.get("product_gate_green") is True,
        "controlled_beta_activation_operational_hold": record.get("controlled_beta_activation_operational_hold") is True,
        "live_learner_traffic_operationally_safe": record.get("live_learner_traffic_operationally_safe") is True,
        "production_release_evidence_blocked_until_runtime_baseline_green": record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        "false_boundaries_locked": boundary_valid,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register_next,
        "production_register_next_authorised_item": prod_next,
        "next_after_evidence": NEXT_AFTER_EVIDENCE,
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
