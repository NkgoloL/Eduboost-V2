"""Audit PRD-11.0R.RUNTIME-RESTORE.EXECUTION-1."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-1"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_1_runtime_command_frontend_generated_contracts_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_1_runtime_command_frontend_generated_contracts.json"
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


def _source_checks(root: Path) -> dict[str, Any]:
    collector = (root / "scripts/production_readiness/collect_prd1100r_true_state_runtime_baseline.py").read_text()
    runtime = (root / "scripts/runtime/verify_runtime_stack_readiness.py").read_text()
    layout = (root / "app/frontend/src/app/(learner)/layout.tsx").read_text()
    frontend_hook_order_valid = (
        "const isParentRoute = pathname.startsWith" in layout
        and "if (!learner && !isParentRoute)" in layout
        and layout.index("useEffect(() =>") < layout.index("if (isParentRoute)")
    )
    return {
        "collector_uses_current_python_interpreter": "import sys" in collector and "sys.executable" in collector,
        "generated_contract_gate_uses_current_interpreter": "[sys.executable, \"scripts/generate_openapi.py\", \"--check\"]" in collector and "[sys.executable, \"scripts/generate_route_inventory.py\", \"--check\"]" in collector,
        "backend_test_gates_use_current_interpreter": "[sys.executable, \"-m\", \"pytest\", \"tests/unit\"" in collector and "[sys.executable, \"-m\", \"pytest\", \"tests/integration\"" in collector,
        "dependency_audit_uses_current_interpreter": "[sys.executable, \"-m\", \"pip_audit\"" in collector,
        "runtime_verifier_uses_current_python_interpreter": "import sys" in runtime and "sys.executable" in runtime,
        "frontend_conditional_hook_repaired": frontend_hook_order_valid,
    }


def _previous_restore_6_valid(root: Path) -> bool:
    record = _load(root / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_6_final_true_state_baseline_handoff_record.json")
    summary = root / "docs/roadmap/production_readiness/prd11_runtime_restore_6_final_true_state_baseline_handoff.json"
    evidence = root / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-6-final-true-state-baseline-handoff/summary.json"
    return all([
        record.get("final_true_state_baseline_handoff_evidence_recorded") is True,
        record.get("next_authorised_item") in {"PRD-11.0R.RUNTIME-RESTORE.EXECUTION", "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-1", "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2"},
        summary.exists(),
        evidence.exists(),
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load(RECORD)
    register = _load(REGISTER)
    prod_register = _load(PROD_REGISTER)
    source = _source_checks(root)
    boundaries_locked = all(record.get(k) is v and register.get(k) is v and prod_register.get(k) is v for k, v in FALSE_BOUNDARIES.items())
    register_agrees = register.get("next_authorised_item") == prod_register.get("next_authorised_item")
    authority_valid = (
        record.get("prd_id") == PRD_ID
        and record.get("authority_recorded") is True
        and all(source.values())
        and boundaries_locked
        and register_agrees
        and _previous_restore_6_valid(root)
    )
    evidence_recorded = record.get("evidence_recorded") is True and SUMMARY.exists()
    valid = authority_valid and evidence_recorded and register.get("next_authorised_item") == "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2" and prod_register.get("next_authorised_item") == "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2"
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "previous_runtime_restore_6_valid": _previous_restore_6_valid(root),
        "source_checks": source,
        **source,
        "runtime_restore_execution_1_authority_recorded": record.get("authority_recorded") is True,
        "runtime_restore_execution_1_evidence_recorded": evidence_recorded,
        "runtime_baseline_green": record.get("runtime_baseline_green") is True,
        "frontend_quality_green": record.get("frontend_quality_green") is True,
        "generated_contracts_green": record.get("generated_contracts_green") is True,
        "controlled_beta_activation_operational_hold": record.get("controlled_beta_activation_operational_hold") is True,
        "live_learner_traffic_operationally_safe": record.get("live_learner_traffic_operationally_safe") is True,
        "production_release_evidence_blocked_until_runtime_baseline_green": record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "false_boundaries_locked": boundaries_locked,
        "registers_agree": register_agrees,
        **{k: record.get(k) for k in FALSE_BOUNDARIES},
    }
