#!/usr/bin/env python3
"""Verify KG-4 gap-engine and intervention-planner authority and captured evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.knowledge_graph.audit_kg004_gap_engine_intervention_planner import audit

KG_ID = "KG-4"
RECORD = Path("docs/roadmap/knowledge_graph/kg_004_gap_engine_intervention_planner_record.json")
KG3_RECORD = Path("docs/roadmap/knowledge_graph/kg_003_learner_graph_shadow_mode_record.json")
BOUNDARY_FALSE_KEYS = [
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "database_schema_migration_authorised",
    "learner_facing_model_change_authorised",
    "learner_graph_implementation_authorised",
    "learner_graph_persistence_authorised",
    "learner_graph_runtime_authority_authorised",
    "gap_engine_runtime_authority_authorised",
    "intervention_planner_runtime_authority_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
]
REQUIRED_TRUE_KEYS = [
    "gap_engine_intervention_planner_recorded",
    "kg3_learner_graph_shadow_mode_valid",
    "shadow_graph_dependency_recorded",
    "target_graph_dependency_recorded",
    "gap_intervention_plan_artifact_generated",
    "synthetic_learner_fixture_only",
    "no_live_learner_data_used",
    "all_gap_items_reference_shadow_states",
    "all_gap_items_source_grounded",
    "all_interventions_source_grounded",
    "all_interventions_advisory_only",
    "duplicate_gap_keys_found_false",
    "duplicate_intervention_keys_found_false",
    "orphan_planner_edges_found_false",
    "advisory_boundary_recorded",
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
    kg3 = read_json(root / KG3_RECORD)
    audit_result = audit(root)
    errors: list[str] = []
    warnings: list[str] = []

    kg3_valid = kg3.get("learner_graph_shadow_mode_recorded") is True and kg3.get("kg_id") == "KG-3"
    if not kg3_valid:
        errors.append("KG-3 learner graph shadow mode must be recorded before KG-4")
    if record.get("kg_id") != KG_ID:
        errors.append("KG-4 record must have kg_id KG-4")
    if not audit_result.get("authority_valid"):
        errors.extend([f"authority audit failed: {err}" for err in audit_result.get("errors", [])])

    captured = record.get("gap_engine_intervention_planner_recorded") is True
    if captured:
        if not audit_result.get("final_valid"):
            errors.extend([f"final KG-4 plan evidence failed: {err}" for err in audit_result.get("errors", [])])
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
        if int(record.get("gap_item_count") or 0) < 200:
            errors.append("KG-4 gap item count must be at least 200")
        if int(record.get("intervention_recommendation_count") or 0) < 200:
            errors.append("KG-4 intervention recommendation count must be at least 200")
    else:
        warnings.append("KG-4 record is still pending evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    authority_errors = [
        e for e in errors
        if not e.startswith("record flag must be true")
        and not e.startswith("final KG-4 plan evidence failed")
        and "gap item count" not in e
        and "intervention recommendation count" not in e
    ]
    authority_valid = not authority_errors and audit_result.get("authority_valid") is True and kg3_valid
    valid = authority_valid and captured and not errors

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "kg_id": KG_ID,
        "record_path": str(RECORD),
        "errors": errors,
        "warnings": warnings,
        "kg3_learner_graph_shadow_mode_valid": kg3_valid,
        "gap_engine_intervention_planner_recorded": captured,
        "shadow_graph_dependency_recorded": record.get("shadow_graph_dependency_recorded") is True,
        "target_graph_dependency_recorded": record.get("target_graph_dependency_recorded") is True,
        "gap_intervention_plan_artifact_generated": record.get("gap_intervention_plan_artifact_generated") is True,
        "synthetic_learner_fixture_only": record.get("synthetic_learner_fixture_only") is True,
        "no_live_learner_data_used": record.get("no_live_learner_data_used") is True,
        "gap_item_count": record.get("gap_item_count"),
        "intervention_recommendation_count": record.get("intervention_recommendation_count"),
        "planner_edge_count": record.get("planner_edge_count"),
        "all_gap_items_reference_shadow_states": record.get("all_gap_items_reference_shadow_states") is True,
        "all_gap_items_source_grounded": record.get("all_gap_items_source_grounded") is True,
        "all_interventions_source_grounded": record.get("all_interventions_source_grounded") is True,
        "all_interventions_advisory_only": record.get("all_interventions_advisory_only") is True,
        "duplicate_gap_keys_found_false": record.get("duplicate_gap_keys_found_false") is True,
        "duplicate_intervention_keys_found_false": record.get("duplicate_intervention_keys_found_false") is True,
        "orphan_planner_edges_found_false": record.get("orphan_planner_edges_found_false") is True,
        "advisory_boundary_recorded": record.get("advisory_boundary_recorded") is True,
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
        print(f"KG-4 gap engine and intervention planner valid: {result['valid']}")
        print(f"KG-4 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
