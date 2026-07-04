#!/usr/bin/env python3
"""Verify RR-016 operational drills authority and captured evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.operations_drills.audit_rr016_operational_drills import audit

RR_ID = "RR-016"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RECORD = Path("docs/roadmap/reconciliation/rr_016_operational_drills_record.json")
RR015_RECORD = Path("docs/roadmap/reconciliation/rr_015_external_approvals_record.json")
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
    "operational_drills_recorded",
    "rr015_external_approvals_valid",
    "backup_drill_completed",
    "restore_drill_completed",
    "rollback_drill_completed",
    "monitoring_dashboard_verified",
    "incident_handoff_verified",
    "rr003_fallback_coverage_caveat_visible",
    "rr006_non_required_checks_caveat_visible",
    "rr017_release_safety_controls_remaining_visible",
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
    rr015 = _json(p(RR015_RECORD))
    register = _read(p(REGISTER))
    errors: list[str] = []
    warnings: list[str] = []

    rr015_valid = rr015.get("external_approvals_recorded") is True and rr015.get("rr_id") == "RR-015"
    register_has_rr016 = RR_ID in register and "Operational drills" in register
    if not register_has_rr016:
        errors.append("RR-016 must remain listed in outstanding_work_register.md")
    if record.get("rr_id") != RR_ID:
        errors.append(f"record rr_id must be {RR_ID}")
    if not rr015_valid:
        errors.append("RR-015 external approvals must be valid before RR-016 capture")
    if not audit_result["authority_valid"]:
        errors.extend([f"authority audit failed: {e}" for e in audit_result.get("errors", [])])

    if record.get("operational_drills_recorded") is True:
        if not audit_result["final_valid"]:
            errors.extend([f"final drill evidence failed: {e}" for e in audit_result.get("errors", [])])
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
    else:
        warnings.append("record is still pending RR-016 evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    authority_errors = [e for e in errors if not e.startswith("record flag must be true") and not e.startswith("final drill evidence failed")]
    authority_valid = not authority_errors and audit_result["authority_valid"] and rr015_valid and register_has_rr016
    valid = authority_valid and record.get("operational_drills_recorded") is True and not errors

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "audit": audit_result,
        "errors": errors,
        "warnings": warnings,
        "rr015_external_approvals_valid": rr015_valid,
        "operational_drills_recorded": record.get("operational_drills_recorded") is True,
        "backup_drill_completed": record.get("backup_drill_completed") is True,
        "restore_drill_completed": record.get("restore_drill_completed") is True,
        "rollback_drill_completed": record.get("rollback_drill_completed") is True,
        "monitoring_dashboard_verified": record.get("monitoring_dashboard_verified") is True,
        "incident_handoff_verified": record.get("incident_handoff_verified") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        "rr006_non_required_checks_caveat_visible": record.get("rr006_non_required_checks_caveat_visible") is True,
        "rr017_release_safety_controls_remaining_visible": record.get("rr017_release_safety_controls_remaining_visible") is True,
        "rr018_trustworthy_beta_quality_remaining_visible": record.get("rr018_trustworthy_beta_quality_remaining_visible") is True,
        **{key: record.get(key) is False for key in BOUNDARY_FALSE_KEYS},
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
        print(f"RR-016 operational drills valid: {result['valid']}")
        print(f"RR-016 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
