#!/usr/bin/env python3
"""Verify KG-3 learner graph shadow-mode authority and captured evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.knowledge_graph.audit_kg003_learner_graph_shadow_mode import audit

KG_ID = "KG-3"
RECORD = Path("docs/roadmap/knowledge_graph/kg_003_learner_graph_shadow_mode_record.json")
KG2_RECORD = Path("docs/roadmap/knowledge_graph/kg_002_target_graph_generation_record.json")
BOUNDARY_FALSE_KEYS = [
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "database_schema_migration_authorised",
    "learner_facing_model_change_authorised",
    "learner_graph_implementation_authorised",
    "learner_graph_persistence_authorised",
    "learner_graph_runtime_authority_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
]
REQUIRED_TRUE_KEYS = [
    "learner_graph_shadow_mode_recorded",
    "kg2_target_graph_generation_valid",
    "target_graph_dependency_recorded",
    "shadow_observation_fixture_recorded",
    "learner_shadow_graph_artifact_generated",
    "synthetic_learner_fixture_only",
    "no_live_learner_data_used",
    "all_shadow_states_reference_targets",
    "all_shadow_states_source_grounded",
    "all_shadow_events_source_grounded",
    "duplicate_shadow_state_keys_found_false",
    "orphan_shadow_edges_found_false",
    "shadow_mode_boundary_recorded",
    "privacy_boundary_recorded",
    "runtime_kg_boundary_recorded",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    record = read_json(root / RECORD)
    kg2 = read_json(root / KG2_RECORD)
    audit_result = audit(root)
    errors: list[str] = []
    warnings: list[str] = []

    kg2_valid = kg2.get("target_graph_generation_recorded") is True and kg2.get("kg_id") == "KG-2"
    if not kg2_valid:
        errors.append("KG-2 target graph generation must be recorded before KG-3")
    if record.get("kg_id") != KG_ID:
        errors.append("KG-3 record must have kg_id KG-3")
    if not audit_result.get("authority_valid"):
        errors.extend([f"authority audit failed: {err}" for err in audit_result.get("errors", [])])

    captured = record.get("learner_graph_shadow_mode_recorded") is True
    if captured:
        if not audit_result.get("final_valid"):
            errors.extend([f"final learner shadow evidence failed: {err}" for err in audit_result.get("errors", [])])
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
        if int(record.get("learner_shadow_state_count") or 0) < 200:
            errors.append("KG-3 learner shadow state count must be at least 200")
        if int(record.get("shadow_evidence_event_count") or 0) < 200:
            errors.append("KG-3 shadow evidence event count must be at least 200")
    else:
        warnings.append("KG-3 record is still pending evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    authority_errors = [
        e for e in errors
        if not e.startswith("record flag must be true")
        and not e.startswith("final learner shadow evidence failed")
        and "state count" not in e
        and "evidence event count" not in e
    ]
    authority_valid = not authority_errors and audit_result.get("authority_valid") is True and kg2_valid
    valid = authority_valid and captured and not errors

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "kg_id": KG_ID,
        "record_path": str(RECORD),
        "errors": errors,
        "warnings": warnings,
        "kg2_target_graph_generation_valid": kg2_valid,
        "learner_graph_shadow_mode_recorded": captured,
        "target_graph_dependency_recorded": record.get("target_graph_dependency_recorded") is True,
        "shadow_observation_fixture_recorded": record.get("shadow_observation_fixture_recorded") is True,
        "learner_shadow_graph_artifact_generated": record.get("learner_shadow_graph_artifact_generated") is True,
        "synthetic_learner_fixture_only": record.get("synthetic_learner_fixture_only") is True,
        "no_live_learner_data_used": record.get("no_live_learner_data_used") is True,
        "learner_shadow_state_count": record.get("learner_shadow_state_count"),
        "shadow_evidence_event_count": record.get("shadow_evidence_event_count"),
        "shadow_edge_count": record.get("shadow_edge_count"),
        "all_shadow_states_reference_targets": record.get("all_shadow_states_reference_targets") is True,
        "all_shadow_states_source_grounded": record.get("all_shadow_states_source_grounded") is True,
        "all_shadow_events_source_grounded": record.get("all_shadow_events_source_grounded") is True,
        "duplicate_shadow_state_keys_found_false": record.get("duplicate_shadow_state_keys_found_false") is True,
        "orphan_shadow_edges_found_false": record.get("orphan_shadow_edges_found_false") is True,
        "shadow_mode_boundary_recorded": record.get("shadow_mode_boundary_recorded") is True,
        "privacy_boundary_recorded": record.get("privacy_boundary_recorded") is True,
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
        print(f"KG-3 learner graph shadow mode valid: {result['valid']}")
        print(f"KG-3 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
