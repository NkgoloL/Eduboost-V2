#!/usr/bin/env python3
"""Verify KG-1 CAPS graph foundation authority and captured evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.knowledge_graph.audit_kg001_caps_graph_foundation import audit

KG_ID = "KG-1"
RECORD = Path("docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation_record.json")
KG0_RECORD = Path("docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval_record.json")
BOUNDARY_FALSE_KEYS = [
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "database_schema_migration_authorised",
    "learner_facing_model_change_authorised",
    "learner_graph_implementation_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
]
REQUIRED_TRUE_KEYS = [
    "caps_graph_foundation_recorded",
    "kg0_formal_roadmap_approval_valid",
    "caps_source_topic_map_present",
    "caps_source_checksum_recorded",
    "caps_graph_artifact_generated",
    "caps_graph_schema_recorded",
    "caps_graph_loader_contract_recorded",
    "caps_graph_review_manifest_recorded",
    "all_caps_nodes_source_grounded",
    "all_caps_edges_source_grounded",
    "duplicate_node_keys_found_false",
    "orphan_edges_found_false",
    "runtime_kg_boundary_recorded",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    record = read_json(root / RECORD)
    kg0 = read_json(root / KG0_RECORD)
    audit_result = audit(root)
    errors: list[str] = []
    warnings: list[str] = []

    kg0_valid = kg0.get("formal_kg_roadmap_approval_recorded") is True and kg0.get("kg_id") == "KG-0"
    if not kg0_valid:
        errors.append("KG-0 formal roadmap approval must be recorded before KG-1")
    if record.get("kg_id") != KG_ID:
        errors.append("KG-1 record must have kg_id KG-1")
    if not audit_result.get("authority_valid"):
        errors.extend([f"authority audit failed: {err}" for err in audit_result.get("errors", [])])

    captured = record.get("caps_graph_foundation_recorded") is True
    if captured:
        if not audit_result.get("final_valid"):
            errors.extend([f"final CAPS graph evidence failed: {err}" for err in audit_result.get("errors", [])])
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
        if int(record.get("caps_graph_node_count") or 0) < 150:
            errors.append("KG-1 node count must be at least 150")
        if int(record.get("caps_graph_edge_count") or 0) < 150:
            errors.append("KG-1 edge count must be at least 150")
    else:
        warnings.append("KG-1 record is still pending evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    authority_errors = [e for e in errors if not e.startswith("record flag must be true") and not e.startswith("final CAPS graph evidence failed") and "node count" not in e and "edge count" not in e]
    authority_valid = not authority_errors and audit_result.get("authority_valid") is True and kg0_valid
    valid = authority_valid and captured and not errors

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "kg_id": KG_ID,
        "record_path": str(RECORD),
        "errors": errors,
        "warnings": warnings,
        "kg0_formal_roadmap_approval_valid": kg0_valid,
        "caps_graph_foundation_recorded": captured,
        "caps_source_checksum_recorded": record.get("caps_source_checksum_recorded") is True,
        "caps_graph_artifact_generated": record.get("caps_graph_artifact_generated") is True,
        "caps_graph_node_count": record.get("caps_graph_node_count"),
        "caps_graph_edge_count": record.get("caps_graph_edge_count"),
        "all_caps_nodes_source_grounded": record.get("all_caps_nodes_source_grounded") is True,
        "all_caps_edges_source_grounded": record.get("all_caps_edges_source_grounded") is True,
        "duplicate_node_keys_found_false": record.get("duplicate_node_keys_found_false") is True,
        "orphan_edges_found_false": record.get("orphan_edges_found_false") is True,
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
        print(f"KG-1 CAPS graph foundation valid: {result['valid']}")
        print(f"KG-1 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
