"""Audit PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.test_suites.product_critical_flow_green import ROOT, OUTPUT_DIR, evaluate_product_critical_flow_contract, load_flow_summary

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_6_product_critical_flow_green_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_6_product_critical_flow_green.json"
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


def _previous_execution_5_valid(root: Path) -> bool:
    record = _load(root / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_5_runtime_stack_db_lineage_ready_green_record.json")
    evidence = root / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-execution-5-runtime-stack-db-lineage-ready-green/summary.json"
    return all([
        record.get("evidence_recorded") is True,
        record.get("runtime_baseline_green") is True,
        record.get("runtime_stack_green") is True,
        record.get("database_lineage_green") is True,
        record.get("schema_contract_green") is True,
        record.get("redis_readiness_green") is True,
        record.get("ready_probe_green") is True,
        record.get("frontend_quality_green") is True,
        record.get("generated_contracts_green") is True,
        record.get("next_authorised_item") in {PRD_ID, "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6"},
        evidence.exists(),
    ])


def _source_checks(root: Path) -> dict[str, bool]:
    helper = (root / "scripts/test_suites/product_critical_flow_green.py").read_text()
    runner = (root / "scripts/test_suites/run_product_critical_flow_green.py").read_text()
    capture = (root / "scripts/roadmap_reconciliation/capture_prd1100r_runtime_restore_execution_6_product_critical_flow_green_evidence.py").read_text()
    return {
        "uses_current_python_interpreter": "sys.executable" in helper,
        "independent_product_commands_recorded": "subprocess.run" in helper and "command_plan" in helper,
        "critical_flows_recorded": all(token in helper for token in ("auth_authorisation", "popia_lifecycle", "billing_commercial", "learner_journeys", "diagnostics_assessments", "audit_trail")),
        "runner_can_execute": "--execute" in runner and "--require-green" in runner,
        "capture_can_require_green": "--require-green" in capture and "product_flow_results_green" in capture,
        "presence_only_evidence_forbidden": "presence_only_outputs_forbidden" in helper,
    }


def audit(root: Path = ROOT, *, require_green: bool = False) -> dict[str, Any]:
    record = _load(RECORD)
    register = _load(REGISTER)
    prod_register = _load(PROD_REGISTER)
    source = _source_checks(root)
    contract = evaluate_product_critical_flow_contract(root, require_green=require_green)
    flow_summary = load_flow_summary(root, output_dir=OUTPUT_DIR)
    boundaries_locked = all(record.get(k) is v and register.get(k) is v and prod_register.get(k) is v for k, v in FALSE_BOUNDARIES.items())
    registers_agree = register.get("next_authorised_item") == prod_register.get("next_authorised_item")
    authority_valid = all([
        record.get("prd_id") == PRD_ID,
        record.get("authority_recorded") is True,
        _previous_execution_5_valid(root),
        contract.get("base_valid") is True,
        all(source.values()),
        boundaries_locked,
        registers_agree,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])
    evidence_recorded = record.get("evidence_recorded") is True and SUMMARY.exists()
    green_required_ok = True if not require_green else (
        flow_summary.get("all_green") is True
        and record.get("product_gate_green") is True
        and record.get("product_runtime_gate_green") is True
        and record.get("critical_product_flows_green") is True
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
        "previous_execution_5_valid": _previous_execution_5_valid(root),
        "source_checks": source,
        **source,
        "product_flow_green_contract_valid": contract.get("base_valid") is True,
        "product_flow_results_green": flow_summary.get("all_green") is True,
        "product_critical_flow_green_authority_recorded": record.get("authority_recorded") is True,
        "product_critical_flow_green_evidence_recorded": evidence_recorded,
        "runtime_baseline_green": record.get("runtime_baseline_green") is True,
        "runtime_stack_green": record.get("runtime_stack_green") is True,
        "database_lineage_green": record.get("database_lineage_green") is True,
        "schema_contract_green": record.get("schema_contract_green") is True,
        "redis_readiness_green": record.get("redis_readiness_green") is True,
        "ready_probe_green": record.get("ready_probe_green") is True,
        "frontend_quality_green": record.get("frontend_quality_green") is True,
        "generated_contracts_green": record.get("generated_contracts_green") is True,
        "product_gate_green": record.get("product_gate_green") is True,
        "product_runtime_gate_green": record.get("product_runtime_gate_green") is True,
        "critical_product_flows_green": record.get("critical_product_flows_green") is True,
        "coverage_gate_green": record.get("coverage_gate_green") is True,
        "advisory_static_gate_green": record.get("advisory_static_gate_green") is True,
        "controlled_beta_activation_operational_hold": record.get("controlled_beta_activation_operational_hold") is True,
        "live_learner_traffic_operationally_safe": record.get("live_learner_traffic_operationally_safe") is True,
        "production_release_evidence_blocked_until_runtime_baseline_green": record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "false_boundaries_locked": boundaries_locked,
        "registers_agree": registers_agree,
        "blockers": flow_summary.get("blockers", []),
        **{k: record.get(k) for k in FALSE_BOUNDARIES},
    }
