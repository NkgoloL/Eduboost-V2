"""Audit PRD-11.0R.RUNTIME-RESTORE-1 runtime stack readiness controls."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.runtime.verify_runtime_stack_readiness import verify_contract

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.0R.RUNTIME-RESTORE-1"
NEXT_AFTER_EVIDENCE = "PRD-11.0R.RUNTIME-RESTORE-2"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_1_runtime_stack_db_lineage_readiness_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_1_runtime_stack_db_lineage_readiness.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-1-runtime-stack-db-lineage-readiness"
REQUIRED_PATHS = [
    "app/core/runtime_readiness.py",
    "app/core/health.py",
    "scripts/runtime/verify_runtime_stack_readiness.py",
    "scripts/production_readiness/collect_prd1100r_true_state_runtime_baseline.py",
    "scripts/production_readiness/audit_prd1100r_runtime_restore_1_runtime_stack_db_lineage_readiness.py",
    "scripts/roadmap_reconciliation/verify_prd1100r_runtime_restore_1_runtime_stack_db_lineage_readiness.py",
    "scripts/roadmap_reconciliation/capture_prd1100r_runtime_restore_1_runtime_stack_db_lineage_readiness_evidence.py",
    "docs/engineering/prd11_runtime_restore_1_runtime_stack_db_lineage_readiness.md",
    "docs/roadmap/production_readiness/prd_1100r_runtime_restore_1_runtime_stack_db_lineage_readiness_record.json",
    "tests/unit/runtime/test_runtime_readiness_contract.py",
    "tests/unit/roadmap_reconciliation/test_prd1100r_runtime_restore_1_runtime_stack_db_lineage_readiness.py",
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
ALLOWED_NEXT = {"PRD-11.0R.RUNTIME-RESTORE", PRD_ID, NEXT_AFTER_EVIDENCE}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd113_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd1103r_coverage_alignment_documentation_defined_closure import audit as audit_prd113
        result = audit_prd113(root)
        return result.get("valid") is True or all([
            result.get("coverage_alignment_evidence_recorded") is True,
            result.get("runtime_restore_handoff_authorised") is True,
            result.get("register_next_authorised_item") in ALLOWED_NEXT,
            result.get("production_register_next_authorised_item") in ALLOWED_NEXT,
        ])
    except Exception:
        return False


def _false_boundaries_preserved(payload: dict[str, Any]) -> bool:
    return all(payload.get(key) is False for key in FALSE_BOUNDARIES)


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load(root / RECORD.relative_to(ROOT))
    register = _load(root / REGISTER.relative_to(ROOT))
    prod = _load(root / PROD_REGISTER.relative_to(ROOT))
    runtime_contract = verify_contract(root, require_live_green=False)
    prod_boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    register_next = register.get("next_authorised_item")
    prod_next = prod.get("next_authorised_item")
    boundary_valid = _false_boundaries_preserved(record) and all(prod_boundaries.get(key) is False for key in FALSE_BOUNDARIES)
    authority_valid = all([
        not missing_paths,
        _previous_prd113_valid(root),
        runtime_contract.get("contract_valid") is True,
        record.get("runtime_stack_db_lineage_readiness_authority_recorded") is True,
        record.get("runtime_stack_contract_controls_installed") is True,
        record.get("exact_migration_head_readiness_required") is True,
        record.get("unknown_alembic_revision_fails_readiness") is True,
        record.get("split_alembic_head_fails_readiness") is True,
        record.get("required_schema_contract_required") is True,
        record.get("diagnostic_irt_columns_required") is True,
        record.get("runtime_kg_tables_required") is True,
        record.get("ready_http_probe_required") is True,
        record.get("docker_compose_stack_contract_required") is True,
        record.get("controlled_beta_activation_operational_hold") is True,
        record.get("live_learner_traffic_operationally_safe") is False,
        record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        boundary_valid,
        register_next in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
        register_next == prod_next,
    ])
    evidence_recorded = record.get("runtime_stack_db_lineage_readiness_evidence_recorded") is True
    baseline_snapshot = record.get("runtime_baseline_snapshot") if isinstance(record.get("runtime_baseline_snapshot"), dict) else {}
    evidence_valid = all([
        evidence_recorded,
        (root / SUMMARY.relative_to(ROOT)).exists(),
        (EVIDENCE_DIR / "summary.json").exists(),
        isinstance(baseline_snapshot.get("checks"), dict),
        "database_lineage_and_schema" in baseline_snapshot.get("hard_gate_names", []),
        "ready_http_probe" in baseline_snapshot.get("hard_gate_names", []),
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
        "previous_prd113_handoff_valid": _previous_prd113_valid(root),
        "runtime_contract_valid": runtime_contract.get("contract_valid") is True,
        "runtime_baseline_green": runtime_contract.get("runtime_baseline_green") is True,
        "runtime_stack_db_lineage_readiness_authority_recorded": record.get("runtime_stack_db_lineage_readiness_authority_recorded") is True,
        "runtime_stack_db_lineage_readiness_evidence_recorded": evidence_recorded,
        "exact_migration_head_readiness_required": record.get("exact_migration_head_readiness_required") is True,
        "required_schema_contract_required": record.get("required_schema_contract_required") is True,
        "ready_http_probe_required": record.get("ready_http_probe_required") is True,
        "docker_compose_stack_contract_required": record.get("docker_compose_stack_contract_required") is True,
        "controlled_beta_activation_operational_hold": record.get("controlled_beta_activation_operational_hold") is True,
        "live_learner_traffic_operationally_safe": record.get("live_learner_traffic_operationally_safe") is True,
        "production_release_evidence_blocked_until_runtime_baseline_green": record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        "false_boundaries_locked": boundary_valid,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register_next,
        "production_register_next_authorised_item": prod_next,
        "next_after_evidence": NEXT_AFTER_EVIDENCE,
        "baseline_blockers": baseline_snapshot.get("blockers", []),
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
