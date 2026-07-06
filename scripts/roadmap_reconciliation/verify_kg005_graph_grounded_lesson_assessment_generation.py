#!/usr/bin/env python3
"""Verify KG-5 graph-grounded lesson and assessment generation authority/evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.knowledge_graph.audit_kg005_graph_grounded_lesson_assessment_generation import audit

KG_ID = "KG-5"
RECORD = Path("docs/roadmap/knowledge_graph/kg_005_graph_grounded_lesson_assessment_generation_record.json")
KG4_RECORD = Path("docs/roadmap/knowledge_graph/kg_004_gap_engine_intervention_planner_record.json")
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
    "generation_runtime_authority_authorised",
    "assessment_runtime_authority_authorised",
    "llm_provider_call_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
]
REQUIRED_TRUE_KEYS = [
    "graph_grounded_generation_recorded",
    "kg4_gap_engine_intervention_planner_valid",
    "gap_plan_dependency_recorded",
    "target_graph_dependency_recorded",
    "generation_pack_artifact_generated",
    "synthetic_learner_fixture_only",
    "no_live_learner_data_used",
    "all_lessons_reference_interventions",
    "all_lessons_source_grounded",
    "all_assessments_reference_lessons",
    "all_assessments_source_grounded",
    "all_generation_items_review_required",
    "all_lessons_advisory_only",
    "all_assessments_advisory_only",
    "duplicate_lesson_keys_found_false",
    "duplicate_assessment_keys_found_false",
    "orphan_generation_edges_found_false",
    "human_review_boundary_recorded",
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
    kg4 = read_json(root / KG4_RECORD)
    audit_result = audit(root)
    errors: list[str] = []
    warnings: list[str] = []

    kg4_valid = kg4.get("gap_engine_intervention_planner_recorded") is True and kg4.get("kg_id") == "KG-4"
    if not kg4_valid:
        errors.append("KG-4 gap engine and intervention planner must be recorded before KG-5")
    if record.get("kg_id") != KG_ID:
        errors.append("KG-5 record must have kg_id KG-5")
    if not audit_result.get("authority_valid"):
        errors.extend([f"authority audit failed: {err}" for err in audit_result.get("errors", [])])

    captured = record.get("graph_grounded_generation_recorded") is True
    if captured:
        if not audit_result.get("final_valid"):
            errors.extend([f"final KG-5 generation evidence failed: {err}" for err in audit_result.get("errors", [])])
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
        if int(record.get("lesson_draft_count") or 0) < 200:
            errors.append("KG-5 lesson draft count must be at least 200")
        if int(record.get("assessment_draft_count") or 0) < 200:
            errors.append("KG-5 assessment draft count must be at least 200")
    else:
        warnings.append("KG-5 record is still pending evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    authority_errors = [
        e for e in errors
        if not e.startswith("record flag must be true")
        and not e.startswith("final KG-5 generation evidence failed")
        and "lesson draft count" not in e
        and "assessment draft count" not in e
    ]
    authority_valid = not authority_errors and audit_result.get("authority_valid") is True and kg4_valid
    valid = authority_valid and captured and not errors

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "kg_id": KG_ID,
        "record_path": str(RECORD),
        "errors": errors,
        "warnings": warnings,
        "kg4_gap_engine_intervention_planner_valid": kg4_valid,
        "graph_grounded_generation_recorded": captured,
        "gap_plan_dependency_recorded": record.get("gap_plan_dependency_recorded") is True,
        "target_graph_dependency_recorded": record.get("target_graph_dependency_recorded") is True,
        "generation_pack_artifact_generated": record.get("generation_pack_artifact_generated") is True,
        "synthetic_learner_fixture_only": record.get("synthetic_learner_fixture_only") is True,
        "no_live_learner_data_used": record.get("no_live_learner_data_used") is True,
        "lesson_draft_count": int(record.get("lesson_draft_count") or 0),
        "assessment_draft_count": int(record.get("assessment_draft_count") or 0),
        "generation_edge_count": int(record.get("generation_edge_count") or 0),
        "all_lessons_reference_interventions": record.get("all_lessons_reference_interventions") is True,
        "all_lessons_source_grounded": record.get("all_lessons_source_grounded") is True,
        "all_assessments_reference_lessons": record.get("all_assessments_reference_lessons") is True,
        "all_assessments_source_grounded": record.get("all_assessments_source_grounded") is True,
        "all_generation_items_review_required": record.get("all_generation_items_review_required") is True,
        "all_lessons_advisory_only": record.get("all_lessons_advisory_only") is True,
        "all_assessments_advisory_only": record.get("all_assessments_advisory_only") is True,
        "duplicate_lesson_keys_found_false": record.get("duplicate_lesson_keys_found_false") is True,
        "duplicate_assessment_keys_found_false": record.get("duplicate_assessment_keys_found_false") is True,
        "orphan_generation_edges_found_false": record.get("orphan_generation_edges_found_false") is True,
        "human_review_boundary_recorded": record.get("human_review_boundary_recorded") is True,
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
        print(f"KG-5 graph-grounded generation valid: {result['valid']}")
        print(f"KG-5 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
