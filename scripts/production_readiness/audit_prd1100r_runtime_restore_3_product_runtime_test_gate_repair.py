"""Audit PRD-11.0R.RUNTIME-RESTORE-3 product/runtime test-gate repair."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.test_suites.product_runtime_gate import evaluate_product_runtime_gate_contract

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.0R.RUNTIME-RESTORE-3"
NEXT_AFTER_EVIDENCE = "PRD-11.0R.RUNTIME-RESTORE-4"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_3_product_runtime_test_gate_repair_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_3_product_runtime_test_gate_repair.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-3-product-runtime-test-gate-repair"
REQUIRED_PATHS = [
    "scripts/test_suites/product_runtime_gate.py",
    "scripts/test_suites/run_product_runtime_gates.py",
    "scripts/test_suites/verify_product_runtime_test_gates.py",
    "scripts/production_readiness/audit_prd1100r_runtime_restore_3_product_runtime_test_gate_repair.py",
    "scripts/roadmap_reconciliation/verify_prd1100r_runtime_restore_3_product_runtime_test_gate_repair.py",
    "scripts/roadmap_reconciliation/capture_prd1100r_runtime_restore_3_product_runtime_test_gate_repair_evidence.py",
    "docs/testing/product_runtime_test_gate_contract.md",
    "docs/engineering/prd11_runtime_restore_3_product_runtime_test_gate_repair.md",
    "docs/roadmap/production_readiness/product_runtime_test_gate_contract.json",
    "docs/roadmap/production_readiness/prd_1100r_runtime_restore_3_product_runtime_test_gate_repair_record.json",
    "tests/unit/test_suites/test_product_runtime_test_gate.py",
    "tests/unit/roadmap_reconciliation/test_prd1100r_runtime_restore_3_product_runtime_test_gate_repair.py",
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
ALLOWED_NEXT = {PRD_ID, NEXT_AFTER_EVIDENCE, "PRD-11.0R.RUNTIME-RESTORE-5"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_restore2_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd1100r_runtime_restore_2_disposable_stack_schema_lineage import audit as audit_restore2
        result = audit_restore2(root)
        return result.get("valid") is True or all([
            result.get("disposable_stack_schema_lineage_evidence_recorded") is True,
            result.get("register_next_authorised_item") in {PRD_ID, NEXT_AFTER_EVIDENCE},
            result.get("production_register_next_authorised_item") in {PRD_ID, NEXT_AFTER_EVIDENCE},
        ])
    except Exception:
        return False


def _false_boundaries_preserved(payload: dict[str, Any]) -> bool:
    return all(payload.get(key) is False for key in FALSE_BOUNDARIES)


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load(root / RECORD.relative_to(ROOT))
    register = _load(root / REGISTER.relative_to(ROOT))
    prod = _load(root / PROD_REGISTER.relative_to(ROOT))
    prod_boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    gate_contract = evaluate_product_runtime_gate_contract(root)
    register_next = register.get("next_authorised_item")
    prod_next = prod.get("next_authorised_item")
    boundary_valid = _false_boundaries_preserved(record) and all(prod_boundaries.get(key) is False for key in FALSE_BOUNDARIES)
    authority_valid = all([
        not missing_paths,
        _previous_restore2_valid(root),
        gate_contract.get("valid") is True,
        record.get("product_runtime_test_gate_authority_recorded") is True,
        record.get("product_runtime_gate_contract_recorded") is True,
        record.get("product_gate_domains_recorded") is True,
        record.get("runtime_gate_domains_recorded") is True,
        record.get("positive_and_negative_paths_required") is True,
        record.get("independent_command_results_required") is True,
        record.get("presence_only_tests_forbidden_as_release_evidence") is True,
        record.get("governance_evidence_substitution_for_product_runtime_forbidden") is True,
        record.get("runtime_baseline_green") is False,
        record.get("product_runtime_gate_green") is False,
        record.get("controlled_beta_activation_operational_hold") is True,
        record.get("live_learner_traffic_operationally_safe") is False,
        record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        boundary_valid,
        register_next in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
        register_next == prod_next,
    ])
    evidence_recorded = record.get("product_runtime_test_gate_evidence_recorded") is True
    evidence_valid = all([
        evidence_recorded,
        (root / SUMMARY.relative_to(ROOT)).exists(),
        (EVIDENCE_DIR / "summary.json").exists(),
        isinstance(record.get("product_runtime_gate_contract_snapshot"), dict),
        record.get("next_authorised_item") in ALLOWED_NEXT,
        register_next in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
    ])
    valid = authority_valid and evidence_valid
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "missing_paths": missing_paths,
        "previous_runtime_restore_2_valid": _previous_restore2_valid(root),
        "product_runtime_gate_contract_valid": gate_contract.get("valid") is True,
        "product_runtime_test_gate_authority_recorded": record.get("product_runtime_test_gate_authority_recorded") is True,
        "product_runtime_test_gate_evidence_recorded": evidence_recorded,
        "product_gate_domains_recorded": record.get("product_gate_domains_recorded") is True,
        "runtime_gate_domains_recorded": record.get("runtime_gate_domains_recorded") is True,
        "positive_and_negative_paths_required": record.get("positive_and_negative_paths_required") is True,
        "independent_command_results_required": record.get("independent_command_results_required") is True,
        "presence_only_tests_forbidden_as_release_evidence": record.get("presence_only_tests_forbidden_as_release_evidence") is True,
        "governance_evidence_substitution_for_product_runtime_forbidden": record.get("governance_evidence_substitution_for_product_runtime_forbidden") is True,
        "runtime_baseline_green": record.get("runtime_baseline_green") is True,
        "product_runtime_gate_green": record.get("product_runtime_gate_green") is True,
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
