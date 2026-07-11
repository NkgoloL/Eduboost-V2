"""Audit PRD-11.0R.RUNTIME-RESTORE-5 coverage/frontend/advisory gate repair."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.advisory_suites.advisory_gate import evaluate_advisory_quality_gate_contract

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.0R.RUNTIME-RESTORE-5"
NEXT_AFTER_EVIDENCE = "PRD-11.0R.RUNTIME-RESTORE-6"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_5_coverage_frontend_advisory_gate_repair_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_5_coverage_frontend_advisory_gate_repair.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-5-coverage-frontend-advisory-gate-repair"
REQUIRED_PATHS = [
    "scripts/advisory_suites/advisory_gate.py",
    "scripts/advisory_suites/run_advisory_quality_gates.py",
    "scripts/advisory_suites/verify_advisory_quality_gates.py",
    "scripts/production_readiness/audit_prd1100r_runtime_restore_5_coverage_frontend_advisory_gate_repair.py",
    "scripts/roadmap_reconciliation/verify_prd1100r_runtime_restore_5_coverage_frontend_advisory_gate_repair.py",
    "scripts/roadmap_reconciliation/capture_prd1100r_runtime_restore_5_coverage_frontend_advisory_gate_repair_evidence.py",
    "docs/testing/coverage_frontend_advisory_gate_contract.md",
    "docs/engineering/prd11_runtime_restore_5_coverage_frontend_advisory_gate_repair.md",
    "docs/roadmap/production_readiness/coverage_frontend_advisory_gate_contract.json",
    "docs/roadmap/production_readiness/prd_1100r_runtime_restore_5_coverage_frontend_advisory_gate_repair_record.json",
    "tests/unit/advisory_suites/test_advisory_quality_gate.py",
    "tests/unit/roadmap_reconciliation/test_prd1100r_runtime_restore_5_coverage_frontend_advisory_gate_repair.py",
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
ALLOWED_NEXT = {PRD_ID, NEXT_AFTER_EVIDENCE}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_restore4_valid(root: Path) -> bool:
    record = _load(root / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_4_product_gate_execution_critical_flow_repair_record.json")
    summary = root / "docs/roadmap/production_readiness/prd11_runtime_restore_4_product_gate_execution_critical_flow_repair.json"
    evidence = root / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-4-product-gate-execution-critical-flow-repair/summary.json"
    return all([
        record.get("product_gate_execution_evidence_recorded") is True,
        record.get("next_authorised_item") in {"PRD-11.0R.RUNTIME-RESTORE-5", "PRD-11.0R.RUNTIME-RESTORE-6"},
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
    contract = evaluate_advisory_quality_gate_contract(root)
    register_next = register.get("next_authorised_item")
    prod_next = prod.get("next_authorised_item")
    boundary_valid = _false_boundaries_preserved(record, prod_boundaries)
    authority_valid = all([
        not missing_paths,
        _previous_restore4_valid(root),
        contract.get("valid") is True,
        record.get("coverage_frontend_advisory_gate_authority_recorded") is True,
        record.get("coverage_frontend_advisory_gate_contract_recorded") is True,
        record.get("coverage_execution_gate_recorded") is True,
        record.get("frontend_quality_gate_recorded") is True,
        record.get("advisory_static_gate_recorded") is True,
        record.get("dependency_security_gate_recorded") is True,
        record.get("generated_contract_drift_gate_recorded") is True,
        record.get("secret_baseline_review_gate_recorded") is True,
        record.get("fresh_coverage_report_required") is True,
        record.get("frontend_lint_vitest_build_required") is True,
        record.get("advisory_static_outputs_required") is True,
        record.get("independent_command_outputs_required") is True,
        record.get("positive_and_negative_or_failure_outputs_required") is True,
        record.get("presence_only_advisory_evidence_forbidden") is True,
        record.get("governance_substitution_for_advisory_forbidden") is True,
        record.get("known_failures_recorded_as_blockers") is True,
        record.get("coverage_gate_green") is False,
        record.get("frontend_quality_green") is False,
        record.get("advisory_static_gate_green") is False,
        record.get("runtime_baseline_green") is False,
        record.get("product_gate_green") is False,
        record.get("controlled_beta_activation_operational_hold") is True,
        record.get("live_learner_traffic_operationally_safe") is False,
        record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        boundary_valid,
        register_next in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
        register_next == prod_next,
    ])
    evidence_recorded = record.get("coverage_frontend_advisory_gate_evidence_recorded") is True
    evidence_valid = all([
        evidence_recorded,
        (root / SUMMARY.relative_to(ROOT)).exists(),
        (EVIDENCE_DIR / "summary.json").exists(),
        isinstance(record.get("coverage_frontend_advisory_gate_contract_snapshot"), dict),
        record.get("next_authorised_item") == NEXT_AFTER_EVIDENCE,
        register_next == NEXT_AFTER_EVIDENCE,
        prod_next == NEXT_AFTER_EVIDENCE,
    ])
    valid = authority_valid and evidence_valid
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "missing_paths": missing_paths,
        "previous_runtime_restore_4_valid": _previous_restore4_valid(root),
        "coverage_frontend_advisory_gate_contract_valid": contract.get("valid") is True,
        "coverage_frontend_advisory_gate_authority_recorded": record.get("coverage_frontend_advisory_gate_authority_recorded") is True,
        "coverage_frontend_advisory_gate_evidence_recorded": evidence_recorded,
        "coverage_execution_gate_recorded": record.get("coverage_execution_gate_recorded") is True,
        "frontend_quality_gate_recorded": record.get("frontend_quality_gate_recorded") is True,
        "advisory_static_gate_recorded": record.get("advisory_static_gate_recorded") is True,
        "dependency_security_gate_recorded": record.get("dependency_security_gate_recorded") is True,
        "generated_contract_drift_gate_recorded": record.get("generated_contract_drift_gate_recorded") is True,
        "secret_baseline_review_gate_recorded": record.get("secret_baseline_review_gate_recorded") is True,
        "fresh_coverage_report_required": record.get("fresh_coverage_report_required") is True,
        "independent_command_outputs_required": record.get("independent_command_outputs_required") is True,
        "presence_only_advisory_evidence_forbidden": record.get("presence_only_advisory_evidence_forbidden") is True,
        "coverage_gate_green": record.get("coverage_gate_green") is True,
        "frontend_quality_green": record.get("frontend_quality_green") is True,
        "advisory_static_gate_green": record.get("advisory_static_gate_green") is True,
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
