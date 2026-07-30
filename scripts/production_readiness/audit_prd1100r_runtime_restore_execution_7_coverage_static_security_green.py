"""Audit PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7."""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import json
from pathlib import Path
from typing import Any

from scripts.advisory_suites.coverage_static_security_green import ROOT, OUTPUT_DIR, evaluate_coverage_static_security_contract, load_summary

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"
PREVIOUS = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_7_coverage_static_security_green_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_7_coverage_static_security_green.json"
FALSE_BOUNDARIES = {
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
    "public_beta_live_traffic_authorised": False,
    "billing_launch_authorised": False,
    "live_payment_processing_authorised": False,
    "prd12_implementation_authorised": False,
}
ALLOWED_NEXT = {PRD_ID, NEXT}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_execution_6_valid(root: Path) -> bool:
    record = _load(root / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_6_product_critical_flow_green_record.json")
    evidence = root / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-execution-6-product-critical-flow-green/summary.json"
    required = (
        "runtime_baseline_green",
        "runtime_stack_green",
        "database_lineage_green",
        "schema_contract_green",
        "redis_readiness_green",
        "ready_probe_green",
        "generated_contracts_green",
        "frontend_quality_green",
        "product_gate_green",
        "product_runtime_gate_green",
        "critical_product_flows_green",
    )
    return all([
        record.get("evidence_recorded") is True,
        all(record.get(field) is True for field in required),
        record.get("next_authorised_item") in {PRD_ID, "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"},
        evidence.exists(),
    ])


def _source_checks(root: Path) -> dict[str, bool]:
    helper = (root / "scripts/advisory_suites/coverage_static_security_green.py").read_text()
    runner = (root / "scripts/advisory_suites/run_coverage_static_security_green.py").read_text()
    capture = (root / "scripts/roadmap_reconciliation/capture_prd1100r_runtime_restore_execution_7_coverage_static_security_green_evidence.py").read_text()
    return {
        "uses_current_python_interpreter": "sys.executable" in helper,
        "independent_commands_recorded": "command_plan" in helper and "scripts._subprocess" in helper,
        "coverage_gate_recorded": "coverage_execution" in helper,
        "static_quality_gates_recorded": all(token in helper for token in ("ruff_release_static_quality", "mypy_release_static_quality", "bandit_release_security")),
        "dependency_and_secret_gates_recorded": all(token in helper for token in ("python_dependency_security_audit", "frontend_dependency_security_audit", "secret_baseline_review")),
        "runner_can_require_green": "--require-green" in helper and "--execute" in helper,
        "capture_can_require_green": "--require-green" in capture and "coverage_static_security_results_green" in capture,
        "wrapper_present": "coverage_static_security_green" in runner,
    }


def audit(root: Path = ROOT, *, require_green: bool = False) -> dict[str, Any]:
    record = _load(RECORD)
    register = _load(REGISTER)
    prod_register = _load(PROD_REGISTER)
    source = _source_checks(root)
    contract = evaluate_coverage_static_security_contract(root, require_green=require_green)
    gate_summary = load_summary(root, output_dir=OUTPUT_DIR)
    boundaries_locked = all(record.get(k) is v and register.get(k) is v and prod_register.get(k) is v for k, v in FALSE_BOUNDARIES.items())
    registers_agree = register.get("next_authorised_item") == prod_register.get("next_authorised_item")
    authority_valid = all([
        record.get("prd_id") == PRD_ID,
        record.get("authority_recorded") is True,
        _previous_execution_6_valid(root),
        contract.get("base_valid") is True,
        all(source.values()),
        boundaries_locked,
        registers_agree,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])
    evidence_recorded = record.get("evidence_recorded") is True and SUMMARY.exists()
    green_required_ok = True if not require_green else (
        gate_summary.get("all_green") is True
        and record.get("coverage_gate_green") is True
        and record.get("advisory_static_gate_green") is True
        and record.get("dependency_audit_gate_green") is True
        and record.get("secret_baseline_gate_green") is True
    )
    valid = all([
        authority_valid,
        evidence_recorded,
        green_required_ok,
        register.get("next_authorised_item") == NEXT,
        prod_register.get("next_authorised_item") == NEXT,
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "previous_execution_6_valid": _previous_execution_6_valid(root),
        "source_checks": source,
        **source,
        "coverage_static_security_contract_valid": contract.get("base_valid") is True,
        "coverage_static_security_results_green": gate_summary.get("all_green") is True,
        "coverage_static_security_authority_recorded": record.get("authority_recorded") is True,
        "coverage_static_security_evidence_recorded": evidence_recorded,
        "runtime_baseline_green": record.get("runtime_baseline_green") is True,
        "product_gate_green": record.get("product_gate_green") is True,
        "generated_contracts_green": record.get("generated_contracts_green") is True,
        "frontend_quality_green": record.get("frontend_quality_green") is True,
        "coverage_gate_green": record.get("coverage_gate_green") is True,
        "advisory_static_gate_green": record.get("advisory_static_gate_green") is True,
        "dependency_audit_gate_green": record.get("dependency_audit_gate_green") is True,
        "secret_baseline_gate_green": record.get("secret_baseline_gate_green") is True,
        "all_advisory_gates_green": record.get("all_advisory_gates_green") is True,
        "controlled_beta_activation_operational_hold": record.get("controlled_beta_activation_operational_hold") is True,
        "live_learner_traffic_operationally_safe": record.get("live_learner_traffic_operationally_safe") is False,
        "production_release_evidence_blocked_until_runtime_baseline_green": record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "false_boundaries_locked": boundaries_locked,
        "registers_agree": registers_agree,
        "blockers": gate_summary.get("blockers", []),
        **{k: record.get(k) for k in FALSE_BOUNDARIES},
    }
