#!/usr/bin/env python3
"""Verify KG roadmap closure report evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.knowledge_graph.audit_kg_roadmap_closure import audit

CLOSURE_ID = "KG-ROADMAP-CLOSURE"
RECORD = Path("docs/roadmap/knowledge_graph/kg_roadmap_closure_record.json")

BOUNDARY_FALSE_KEYS = [
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    record = read_json(root / RECORD)
    audit_result = audit(root)
    errors = list(audit_result.get("errors", []))
    warnings = list(audit_result.get("warnings", []))

    if record.get("closure_id") not in (None, CLOSURE_ID):
        errors.append("closure record must identify KG-ROADMAP-CLOSURE")

    captured = record.get("kg_roadmap_closure_recorded") is True
    if captured:
        if record.get("closure_id") != CLOSURE_ID:
            errors.append("captured closure record must identify KG-ROADMAP-CLOSURE")
        for key in [
            "all_kg_items_closed_through_kg8",
            "kgact001_activation_gate_closed",
            "kg8_post_switch_review_closed",
            "kg_roadmap_completed_through_kg8",
            "kg008_non_required_check_pytest_path_caveat_visible",
            "kg_roadmap_closed_no_new_kg_slice_authorised",
        ]:
            if record.get(key) is not True:
                errors.append(f"closure record flag must be true: {key}")
        for key in BOUNDARY_FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"boundary flag must remain false: {key}")
    else:
        warnings.append("KG roadmap closure evidence has not been captured yet")

    authority_errors = [
        error for error in errors
        if not error.startswith("closure record flag must be true")
        and not error.startswith("boundary flag must remain false")
        and "captured closure record" not in error
    ]
    authority_valid = audit_result.get("authority_valid") is True and not authority_errors
    valid = authority_valid and captured and not errors
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "closure_id": CLOSURE_ID,
        "record_path": str(RECORD),
        "errors": errors,
        "warnings": warnings,
        "kg_roadmap_closure_recorded": captured,
        "all_kg_items_closed_through_kg8": record.get("all_kg_items_closed_through_kg8") is True,
        "kg_item_count": int(record.get("kg_item_count") or audit_result.get("kg_item_count") or 0),
        "kgact001_activation_gate_closed": record.get("kgact001_activation_gate_closed") is True,
        "kg8_post_switch_review_closed": record.get("kg8_post_switch_review_closed") is True,
        "kg_roadmap_completed_through_kg8": record.get("kg_roadmap_completed_through_kg8") is True,
        "kg008_non_required_check_pytest_path_caveat_visible": record.get("kg008_non_required_check_pytest_path_caveat_visible") is True,
        "kg_roadmap_closed_no_new_kg_slice_authorised": record.get("kg_roadmap_closed_no_new_kg_slice_authorised") is True,
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed"),
        "runtime_kg_authority_switch_authorised": record.get("runtime_kg_authority_switch_authorised"),
        "authority_switch_executed": record.get("authority_switch_executed"),
        "production_release_authorised": record.get("production_release_authorised"),
        "deployment_authorised": record.get("deployment_authorised"),
        "release_tag_authorised": record.get("release_tag_authorised"),
        "public_beta_authorised": record.get("public_beta_authorised"),
        "public_beta_live_traffic_authorised": record.get("public_beta_live_traffic_authorised"),
        "billing_launch_authorised": record.get("billing_launch_authorised"),
        "live_payment_processing_authorised": record.get("live_payment_processing_authorised"),
        "kg8_counts": audit_result.get("kg8_counts", {}),
        "audit": audit_result,
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
        print(f"KG roadmap closure valid: {result['valid']}")
        print(f"KG roadmap closure authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
