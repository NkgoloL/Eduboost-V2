"""Audit PRD-11.0R.RUNTIME-RESTORE-2 disposable stack/schema-lineage controls."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.runtime.disposable_stack_lineage import verify_disposable_stack_lineage_contract

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.0R.RUNTIME-RESTORE-2"
NEXT_AFTER_EVIDENCE = "PRD-11.0R.RUNTIME-RESTORE-3"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_2_disposable_stack_schema_lineage_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_2_disposable_stack_schema_lineage.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-2-disposable-stack-schema-lineage"
REQUIRED_PATHS = [
    "scripts/runtime/disposable_stack_lineage.py",
    "scripts/runtime/verify_disposable_stack_schema_lineage.py",
    "scripts/production_readiness/collect_prd1100r_true_state_runtime_baseline.py",
    "scripts/production_readiness/audit_prd1100r_runtime_restore_2_disposable_stack_schema_lineage.py",
    "scripts/roadmap_reconciliation/verify_prd1100r_runtime_restore_2_disposable_stack_schema_lineage.py",
    "scripts/roadmap_reconciliation/capture_prd1100r_runtime_restore_2_disposable_stack_schema_lineage_evidence.py",
    "docs/engineering/prd11_runtime_restore_2_disposable_stack_schema_lineage.md",
    "docs/roadmap/production_readiness/prd_1100r_runtime_restore_2_disposable_stack_schema_lineage_record.json",
    "tests/unit/runtime/test_disposable_stack_schema_lineage.py",
    "tests/unit/roadmap_reconciliation/test_prd1100r_runtime_restore_2_disposable_stack_schema_lineage.py",
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
ALLOWED_NEXT = {"PRD-11.0R.RUNTIME-RESTORE-2", NEXT_AFTER_EVIDENCE}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_restore1_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd1100r_runtime_restore_1_runtime_stack_db_lineage_readiness import audit as audit_restore1
        result = audit_restore1(root)
        return result.get("valid") is True or all([
            result.get("runtime_stack_db_lineage_readiness_evidence_recorded") is True,
            result.get("register_next_authorised_item") in {"PRD-11.0R.RUNTIME-RESTORE-2", NEXT_AFTER_EVIDENCE},
            result.get("production_register_next_authorised_item") in {"PRD-11.0R.RUNTIME-RESTORE-2", NEXT_AFTER_EVIDENCE},
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
    contract = verify_disposable_stack_lineage_contract(root, require_live=False)
    register_next = register.get("next_authorised_item")
    prod_next = prod.get("next_authorised_item")
    boundary_valid = _false_boundaries_preserved(record) and all(prod_boundaries.get(key) is False for key in FALSE_BOUNDARIES)
    authority_valid = all([
        not missing_paths,
        _previous_restore1_valid(root),
        contract.get("contract_valid") is True,
        record.get("disposable_stack_schema_lineage_authority_recorded") is True,
        record.get("fresh_disposable_database_must_migrate_to_head") is True,
        record.get("no_blind_alembic_stamp") is True,
        record.get("snapshot_before_lineage_repair") is True,
        record.get("existing_database_inventory_required_before_bridge_or_rebuild") is True,
        record.get("schema_contract_required_after_migration") is True,
        record.get("ready_probe_required_after_stack_start") is True,
        record.get("controlled_beta_activation_operational_hold") is True,
        record.get("live_learner_traffic_operationally_safe") is False,
        record.get("production_release_evidence_blocked_until_runtime_baseline_green") is True,
        boundary_valid,
        register_next in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
        register_next == prod_next,
    ])
    evidence_recorded = record.get("disposable_stack_schema_lineage_evidence_recorded") is True
    evidence_valid = all([
        evidence_recorded,
        (root / SUMMARY.relative_to(ROOT)).exists(),
        (EVIDENCE_DIR / "summary.json").exists(),
        isinstance(record.get("disposable_stack_schema_lineage_contract_snapshot"), dict),
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
        "previous_runtime_restore_1_valid": _previous_restore1_valid(root),
        "disposable_stack_schema_lineage_contract_valid": contract.get("contract_valid") is True,
        "live_lineage_schema_green": contract.get("live_lineage_schema_green") is True,
        "disposable_stack_schema_lineage_authority_recorded": record.get("disposable_stack_schema_lineage_authority_recorded") is True,
        "disposable_stack_schema_lineage_evidence_recorded": evidence_recorded,
        "fresh_disposable_database_must_migrate_to_head": record.get("fresh_disposable_database_must_migrate_to_head") is True,
        "no_blind_alembic_stamp": record.get("no_blind_alembic_stamp") is True,
        "snapshot_before_lineage_repair": record.get("snapshot_before_lineage_repair") is True,
        "existing_database_inventory_required_before_bridge_or_rebuild": record.get("existing_database_inventory_required_before_bridge_or_rebuild") is True,
        "schema_contract_required_after_migration": record.get("schema_contract_required_after_migration") is True,
        "ready_probe_required_after_stack_start": record.get("ready_probe_required_after_stack_start") is True,
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
