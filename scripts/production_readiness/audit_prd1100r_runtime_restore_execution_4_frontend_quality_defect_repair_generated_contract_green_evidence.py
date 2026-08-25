"""Audit PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.advisory_suites.generated_contract_frontend_quality_green_evidence import (
    DEFAULT_OUTPUT_DIR,
    evaluate_green_evidence_contract,
    load_green_evidence_summary,
)

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5"
ALLOWED_NEXT = {NEXT, "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6", "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7", "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8"}
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_4_frontend_quality_defect_repair_generated_contract_green_evidence_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_4_frontend_quality_defect_repair_generated_contract_green_evidence.json"
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


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_execution_3_valid(root: Path) -> bool:
    record = _load(root / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_3_generated_contract_frontend_green_run_record.json")
    summary = root / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_3_generated_contract_frontend_green_run.json"
    evidence = root / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-execution-3-generated-contract-frontend-green-run/summary.json"
    return all([
        record.get("evidence_recorded") is True,
        record.get("next_authorised_item") in {PRD_ID, "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4"},
        summary.exists(),
        evidence.exists(),
    ])


def _source_checks(root: Path) -> dict[str, bool]:
    helper = (root / "scripts/advisory_suites/generated_contract_frontend_quality_green_evidence.py").read_text()
    runner = (root / "scripts/advisory_suites/run_generated_contract_frontend_quality_green_evidence.py").read_text()
    frontend_package = (root / "app/frontend/package.json").read_text()
    next_config = (root / "app/frontend/next.config.js").read_text()
    return {
        "green_evidence_uses_current_python_interpreter": "sys.executable" in helper and "scripts/generate_openapi.py" in helper,
        "openapi_route_inventory_green_evidence_recorded": "scripts/generate_route_inventory.py" in helper and "--check" in helper,
        "frontend_quality_release_gate_recorded": "quality:release" in helper and "frontend_release_quality" in helper,
        "frontend_release_lint_is_error_blocking_not_warning_blocking": "lint:release" in frontend_package and "lint:strict" in frontend_package,
        "frontend_build_side_effect_check_recorded": "frontend_build_side_effect_check" in helper and "next-env.d.ts" in helper and "public/sw.js" in helper,
        "service_worker_generation_explicitly_opt_in": "EDUBOOST_GENERATE_SERVICE_WORKER" in next_config,
        "runner_can_execute_and_list_commands": "--execute" in runner and "green_evidence_command_plan" in runner,
    }


def audit(root: Path = ROOT, *, require_green: bool = False) -> dict[str, Any]:
    record = _load(RECORD)
    register = _load(REGISTER)
    prod_register = _load(PROD_REGISTER)
    source = _source_checks(root)
    contract = evaluate_green_evidence_contract(root, require_green=require_green)
    green_summary = {
        "all_green": contract.get("all_green") is True,
        "generated_contracts_green": contract.get("generated_contracts_green") is True,
        "frontend_quality_green": contract.get("frontend_quality_green") is True,
        "blockers": contract.get("blockers", []),
    }
    boundaries_locked = all(record.get(k) is v and register.get(k) is v and prod_register.get(k) is v for k, v in FALSE_BOUNDARIES.items())
    registers_agree = register.get("next_authorised_item") == prod_register.get("next_authorised_item")
    authority_valid = all([
        record.get("prd_id") == PRD_ID,
        record.get("authority_recorded") is True,
        _previous_execution_3_valid(root),
        contract.get("base_valid") is True,
        all(source.values()),
        boundaries_locked,
        registers_agree,
    ])
    evidence_recorded = contract.get("results_valid") is True and contract.get("all_green") is True
    green_required_ok = True if not require_green else (
        green_summary.get("all_green") is True
        and green_summary.get("generated_contracts_green") is True
        and green_summary.get("frontend_quality_green") is True
    )
    valid = all([
        authority_valid,
        evidence_recorded,
        green_required_ok,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "previous_execution_3_valid": _previous_execution_3_valid(root),
        "source_checks": source,
        **source,
        "green_evidence_contract_valid": contract.get("base_valid") is True,
        "green_evidence_results_green": green_summary.get("all_green") is True,
        "frontend_quality_defect_repair_authority_recorded": record.get("authority_recorded") is True,
        "frontend_quality_defect_repair_evidence_recorded": evidence_recorded,
        "generated_contracts_green": contract.get("generated_contracts_green") is True,
        "frontend_quality_green": contract.get("frontend_quality_green") is True,
        "runtime_baseline_green": record.get("runtime_baseline_green") is True,
        "controlled_beta_activation_operational_hold": record.get("controlled_beta_activation_operational_hold") is True,
        "live_learner_traffic_operationally_safe": record.get("live_learner_traffic_operationally_safe") is True,
        "production_release_evidence_blocked_until_runtime_baseline_green": record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "false_boundaries_locked": boundaries_locked,
        "registers_agree": registers_agree,
        "blockers": green_summary.get("blockers", []),
        **{k: record.get(k) for k in FALSE_BOUNDARIES},
    }
