"""Audit PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.advisory_suites.generated_frontend_quality_gate import evaluate_generated_frontend_quality_contract

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_2_generated_contract_frontend_quality_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_2_generated_contract_frontend_quality.json"
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


def _previous_execution_1_valid(root: Path) -> bool:
    record = _load(root / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_1_runtime_command_frontend_generated_contracts_record.json")
    summary = root / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_1_runtime_command_frontend_generated_contracts.json"
    evidence = root / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-execution-1-runtime-command-frontend-generated-contracts/summary.json"
    return all([
        record.get("evidence_recorded") is True,
        record.get("next_authorised_item") in {PRD_ID, "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2"},
        summary.exists(),
        evidence.exists(),
    ])


def _source_checks(root: Path) -> dict[str, bool]:
    runner = (root / "scripts/advisory_suites/generated_frontend_quality_gate.py").read_text()
    package = json.loads((root / "app/frontend/package.json").read_text())
    scripts = package.get("scripts", {})
    advisory = (root / "scripts/advisory_suites/advisory_gate.py").read_text()
    final = (root / "scripts/runtime/final_true_state_baseline.py").read_text()
    return {
        "gate_runner_uses_current_python_interpreter": "sys.executable" in runner and "scripts/generate_openapi.py" in runner,
        "generated_contract_read_only_check_recorded": "--check" in runner and "scripts/generate_route_inventory.py" in runner,
        "frontend_release_quality_script_recorded": "quality:release" in scripts and "lint:strict" in scripts,
        "frontend_quality_uses_existing_test_script": "pnpm run test" in advisory and "pnpm run test" in final and "pnpm test:run" not in advisory and "pnpm test:run" not in final,
        "generated_contract_commands_have_python_fallback": "${PYTHON:-python3} scripts/generate_openapi.py --check" in advisory and "${PYTHON:-python3} scripts/generate_openapi.py --check" in final,
    }


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load(RECORD)
    register = _load(REGISTER)
    prod_register = _load(PROD_REGISTER)
    source = _source_checks(root)
    contract = evaluate_generated_frontend_quality_contract(root)
    boundaries_locked = all(record.get(k) is v and register.get(k) is v and prod_register.get(k) is v for k, v in FALSE_BOUNDARIES.items())
    register_agrees = register.get("next_authorised_item") == prod_register.get("next_authorised_item")
    authority_valid = all([
        record.get("prd_id") == PRD_ID,
        record.get("authority_recorded") is True,
        _previous_execution_1_valid(root),
        contract.get("valid") is True,
        all(source.values()),
        boundaries_locked,
        register_agrees,
    ])
    evidence_recorded = record.get("evidence_recorded") is True and SUMMARY.exists()
    valid = all([
        authority_valid,
        evidence_recorded,
        register.get("next_authorised_item") == NEXT,
        prod_register.get("next_authorised_item") == NEXT,
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "previous_execution_1_valid": _previous_execution_1_valid(root),
        "source_checks": source,
        **source,
        "generated_frontend_contract_valid": contract.get("valid") is True,
        "generated_contract_frontend_quality_authority_recorded": record.get("authority_recorded") is True,
        "generated_contract_frontend_quality_evidence_recorded": evidence_recorded,
        "generated_contracts_green": record.get("generated_contracts_green") is True,
        "frontend_quality_green": record.get("frontend_quality_green") is True,
        "runtime_baseline_green": record.get("runtime_baseline_green") is True,
        "controlled_beta_activation_operational_hold": record.get("controlled_beta_activation_operational_hold") is True,
        "live_learner_traffic_operationally_safe": record.get("live_learner_traffic_operationally_safe") is True,
        "production_release_evidence_blocked_until_runtime_baseline_green": record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "false_boundaries_locked": boundaries_locked,
        "registers_agree": register_agrees,
        **{k: record.get(k) for k in FALSE_BOUNDARIES},
    }
