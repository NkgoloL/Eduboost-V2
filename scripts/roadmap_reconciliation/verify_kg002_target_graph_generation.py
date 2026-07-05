#!/usr/bin/env python3
"""Verify KG-2 target graph generation authority and captured evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.knowledge_graph.audit_kg002_target_graph_generation import audit

KG_ID = "KG-2"
RECORD = Path("docs/roadmap/knowledge_graph/kg_002_target_graph_generation_record.json")
KG1_RECORD = Path("docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation_record.json")
BOUNDARY_FALSE_KEYS = [
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "database_schema_migration_authorised",
    "learner_facing_model_change_authorised",
    "learner_graph_implementation_authorised",
    "target_graph_runtime_authority_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
]
REQUIRED_TRUE_KEYS = [
    "target_graph_generation_recorded",
    "kg1_caps_graph_foundation_valid",
    "caps_graph_dependency_recorded",
    "target_graph_artifact_generated",
    "target_graph_schema_recorded",
    "target_graph_policy_contract_recorded",
    "target_graph_review_manifest_recorded",
    "target_graph_references_approved_caps_nodes_only",
    "required_mastery_thresholds_present",
    "required_confidence_thresholds_present",
    "priority_weighting_present",
    "pacing_windows_present",
    "duplicate_target_keys_found_false",
    "orphan_target_edges_found_false",
    "runtime_kg_boundary_recorded",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    record = read_json(root / RECORD)
    kg1 = read_json(root / KG1_RECORD)
    audit_result = audit(root)
    errors: list[str] = []
    warnings: list[str] = []

    kg1_valid = kg1.get("caps_graph_foundation_recorded") is True and kg1.get("kg_id") == "KG-1"
    if not kg1_valid:
        errors.append("KG-1 CAPS graph foundation must be recorded before KG-2")
    if record.get("kg_id") != KG_ID:
        errors.append("KG-2 record must have kg_id KG-2")
    if not audit_result.get("authority_valid"):
        errors.extend([f"authority audit failed: {err}" for err in audit_result.get("errors", [])])

    captured = record.get("target_graph_generation_recorded") is True
    if captured:
        if not audit_result.get("final_valid"):
            errors.extend([f"final target graph evidence failed: {err}" for err in audit_result.get("errors", [])])
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
        if int(record.get("target_graph_state_count") or 0) < 100:
            errors.append("KG-2 target graph state count must be at least 100")
        if int(record.get("target_graph_edge_count") or 0) < 100:
            errors.append("KG-2 target graph edge count must be at least 100")
    else:
        warnings.append("KG-2 record is still pending evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    authority_errors = [
        e for e in errors
        if not e.startswith("record flag must be true") and not e.startswith("final target graph evidence failed") and "state count" not in e and "edge count" not in e
    ]
    authority_valid = not authority_errors and audit_result.get("authority_valid") is True and kg1_valid
    valid = authority_valid and captured and not errors

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "kg_id": KG_ID,
        "record_path": str(RECORD),
        "errors": errors,
        "warnings": warnings,
        "kg1_caps_graph_foundation_valid": kg1_valid,
        "target_graph_generation_recorded": captured,
        "caps_graph_dependency_recorded": record.get("caps_graph_dependency_recorded") is True,
        "target_graph_artifact_generated": record.get("target_graph_artifact_generated") is True,
        "target_graph_state_count": record.get("target_graph_state_count"),
        "target_graph_edge_count": record.get("target_graph_edge_count"),
        "target_graph_references_approved_caps_nodes_only": record.get("target_graph_references_approved_caps_nodes_only") is True,
        "required_mastery_thresholds_present": record.get("required_mastery_thresholds_present") is True,
        "required_confidence_thresholds_present": record.get("required_confidence_thresholds_present") is True,
        "priority_weighting_present": record.get("priority_weighting_present") is True,
        "pacing_windows_present": record.get("pacing_windows_present") is True,
        "duplicate_target_keys_found_false": record.get("duplicate_target_keys_found_false") is True,
        "orphan_target_edges_found_false": record.get("orphan_target_edges_found_false") is True,
        "runtime_kg_boundary_recorded": record.get("runtime_kg_boundary_recorded") is True,
        "audit": audit_result,
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
        print(f"KG-2 target graph generation valid: {result['valid']}")
        print(f"KG-2 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
