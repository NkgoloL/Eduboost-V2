"""Audit PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.runtime.runtime_stack_db_ready_green import DEFAULT_OUTPUT_DIR, ROOT, evaluate_runtime_green_contract, load_runtime_green_summary

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_5_runtime_stack_db_lineage_ready_green_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_5_runtime_stack_db_lineage_ready_green.json"
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
ALLOWED_NEXT = {PRD_ID, NEXT, "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7", "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_execution_4_valid(root: Path) -> bool:
    record = _load(root / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_4_frontend_quality_defect_repair_generated_contract_green_evidence_record.json")
    summary = root / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_4_frontend_quality_defect_repair_generated_contract_green_evidence.json"
    evidence = root / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-execution-4-frontend-quality-defect-repair-generated-contract-green-evidence/summary.json"
    return all([
        record.get("evidence_recorded") is True,
        record.get("generated_contracts_green") is True,
        record.get("frontend_quality_green") is True,
        record.get("next_authorised_item") in {PRD_ID, "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5"},
        summary.exists(),
        evidence.exists(),
    ])


def _source_checks(root: Path) -> dict[str, bool]:
    helper = (root / "scripts/runtime/runtime_stack_db_ready_green.py").read_text()
    runner = (root / "scripts/runtime/run_runtime_stack_db_ready_green.py").read_text()
    capture = (root / "scripts/roadmap_reconciliation/capture_prd1100r_runtime_restore_execution_5_runtime_stack_db_lineage_ready_green_evidence.py").read_text()
    return {
        "runtime_green_uses_current_python_interpreter": "sys.executable" in helper and "verify_disposable_stack_schema_lineage.py" in helper,
        "alembic_upgrade_head_required": "alembic_upgrade_head" in helper and "--apply-migrations" in helper,
        "live_schema_lineage_required": "disposable_stack_schema_lineage_live" in helper and "--require-live" in helper,
        "redis_readiness_required": "redis_readiness" in helper and "REDIS_URL" in helper,
        "ready_http_probe_required": "ready_http_probe" in helper and "/ready" in helper,
        "runner_can_execute": "main" in runner and "--execute" in helper,
        "capture_can_require_green": "--require-green" in capture and "all_green" in capture,
    }


def audit(root: Path = ROOT, *, require_green: bool = False) -> dict[str, Any]:
    record = _load(RECORD)
    register = _load(REGISTER)
    prod_register = _load(PROD_REGISTER)
    source = _source_checks(root)
    contract = evaluate_runtime_green_contract(root, require_green=require_green)
    green_summary = load_runtime_green_summary(root, output_dir=DEFAULT_OUTPUT_DIR)
    boundaries_locked = all(record.get(k) is v and register.get(k) is v and prod_register.get(k) is v for k, v in FALSE_BOUNDARIES.items())
    registers_agree = register.get("next_authorised_item") == prod_register.get("next_authorised_item")
    authority_valid = all([
        record.get("prd_id") == PRD_ID,
        record.get("authority_recorded") is True,
        _previous_execution_4_valid(root),
        contract.get("base_valid") is True,
        all(source.values()),
        boundaries_locked,
        registers_agree,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])
    evidence_recorded = record.get("evidence_recorded") is True and SUMMARY.exists()
    green_required_ok = True if not require_green else (
        green_summary.get("all_green") is True
        and record.get("runtime_stack_green") is True
        and record.get("database_lineage_green") is True
        and record.get("schema_contract_green") is True
        and record.get("redis_readiness_green") is True
        and record.get("ready_probe_green") is True
    )
    valid = all([
        authority_valid,
        evidence_recorded,
        green_required_ok,
        register.get("next_authorised_item") in {NEXT, "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"},
        prod_register.get("next_authorised_item") in {NEXT, "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"},
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "previous_execution_4_valid": _previous_execution_4_valid(root),
        "source_checks": source,
        **source,
        "runtime_green_contract_valid": contract.get("base_valid") is True,
        "runtime_green_results_green": green_summary.get("all_green") is True,
        "runtime_stack_db_lineage_ready_green_authority_recorded": record.get("authority_recorded") is True,
        "runtime_stack_db_lineage_ready_green_evidence_recorded": evidence_recorded,
        "runtime_stack_green": record.get("runtime_stack_green") is True,
        "database_lineage_green": record.get("database_lineage_green") is True,
        "schema_contract_green": record.get("schema_contract_green") is True,
        "redis_readiness_green": record.get("redis_readiness_green") is True,
        "ready_probe_green": record.get("ready_probe_green") is True,
        "runtime_baseline_green": record.get("runtime_baseline_green") is True,
        "product_gate_green": record.get("product_gate_green") is True,
        "coverage_gate_green": record.get("coverage_gate_green") is True,
        "frontend_quality_green": record.get("frontend_quality_green") is True,
        "generated_contracts_green": record.get("generated_contracts_green") is True,
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


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--authority-only", action="store_true")
    parser.add_argument("--require-green", action="store_true")
    args = parser.parse_args()
    result = audit(ROOT, require_green=args.require_green and not args.authority_only)
    if args.authority_only:
        result = {**result, "valid": False}
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    raise SystemExit(0 if (result.get("authority_valid") if args.authority_only else result.get("valid")) else 1)
