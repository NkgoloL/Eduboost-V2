#!/usr/bin/env python3
"""Verify RR-017 release safety controls authority and captured evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.release_safety.audit_rr017_release_safety_controls import audit

RR_ID = "RR-017"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RECORD = Path("docs/roadmap/reconciliation/rr_017_release_safety_controls_record.json")
RR016_RECORD = Path("docs/roadmap/reconciliation/rr_016_operational_drills_record.json")
BOUNDARY_FALSE_KEYS = [
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "runtime_kg_implementation_claimed",
]
REQUIRED_TRUE_KEYS = [
    "release_safety_controls_recorded",
    "rr016_operational_drills_valid",
    "release_safety_controls_attested",
    "destructive_audit_consent_db_changes_blocked",
    "alembic_stamp_head_repair_blocked",
    "production_db_mutation_requires_migration_window",
    "mutating_health_probes_blocked",
    "prohibited_operations_register_recorded",
    "migration_window_control_recorded",
    "health_probe_immutability_validated",
    "release_change_control_boundary_recorded",
    "break_glass_exception_process_recorded",
    "rr003_fallback_coverage_caveat_visible",
    "rr006_non_required_checks_caveat_visible",
    "rr016_clean_git_state_caveat_visible",
    "rr018_trustworthy_beta_quality_remaining_visible",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)

    def p(path: Path) -> Path:
        return root / path

    audit_result = audit(root)
    record = _json(p(RECORD))
    rr016 = _json(p(RR016_RECORD))
    register = _read(p(REGISTER))
    errors: list[str] = []
    warnings: list[str] = []

    rr016_valid = rr016.get("operational_drills_recorded") is True and rr016.get("rr_id") == "RR-016"
    register_has_rr017 = RR_ID in register and "Production deployment blockers" in register
    if not register_has_rr017:
        errors.append("RR-017 must remain listed in outstanding_work_register.md")
    if record.get("rr_id") != RR_ID:
        errors.append(f"record rr_id must be {RR_ID}")
    if not rr016_valid:
        errors.append("RR-016 operational drills must be valid before RR-017 capture")
    if not audit_result["authority_valid"]:
        errors.extend([f"authority audit failed: {e}" for e in audit_result.get("errors", [])])

    if record.get("release_safety_controls_recorded") is True:
        if not audit_result["final_valid"]:
            errors.extend([f"final release-safety evidence failed: {e}" for e in audit_result.get("errors", [])])
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
    else:
        warnings.append("record is still pending RR-017 evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    authority_errors = [
        e for e in errors
        if not e.startswith("record flag must be true") and not e.startswith("final release-safety evidence failed")
    ]
    authority_valid = not authority_errors and audit_result["authority_valid"] and rr016_valid and register_has_rr017
    valid = authority_valid and record.get("release_safety_controls_recorded") is True and not errors
    if record.get("release_safety_controls_recorded") is not True:
        valid = False

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "audit": audit_result,
        "errors": errors,
        "warnings": warnings,
        "rr016_operational_drills_valid": rr016_valid,
        "release_safety_controls_recorded": record.get("release_safety_controls_recorded") is True,
        "release_safety_controls_attested": record.get("release_safety_controls_attested") is True,
        "destructive_audit_consent_db_changes_blocked": record.get("destructive_audit_consent_db_changes_blocked") is True,
        "alembic_stamp_head_repair_blocked": record.get("alembic_stamp_head_repair_blocked") is True,
        "production_db_mutation_requires_migration_window": record.get("production_db_mutation_requires_migration_window") is True,
        "mutating_health_probes_blocked": record.get("mutating_health_probes_blocked") is True,
        "prohibited_operations_register_recorded": record.get("prohibited_operations_register_recorded") is True,
        "migration_window_control_recorded": record.get("migration_window_control_recorded") is True,
        "health_probe_immutability_validated": record.get("health_probe_immutability_validated") is True,
        "release_change_control_boundary_recorded": record.get("release_change_control_boundary_recorded") is True,
        "break_glass_exception_process_recorded": record.get("break_glass_exception_process_recorded") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        "rr006_non_required_checks_caveat_visible": record.get("rr006_non_required_checks_caveat_visible") is True,
        "rr016_clean_git_state_caveat_visible": record.get("rr016_clean_git_state_caveat_visible") is True,
        "rr018_trustworthy_beta_quality_remaining_visible": record.get("rr018_trustworthy_beta_quality_remaining_visible") is True,
        **{key: record.get(key) for key in BOUNDARY_FALSE_KEYS},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--authority-only", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"RR-017 release safety controls valid: {result['valid']}")
        print(f"RR-017 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
