#!/usr/bin/env python3
"""Verify KG-6 tutor/study-plan/gamification/parent alignment authority/evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.knowledge_graph.audit_kg006_tutor_study_plan_gamification_parent_alignment import audit

KG_ID = "KG-6"
RECORD = Path("docs/roadmap/knowledge_graph/kg_006_tutor_study_plan_gamification_parent_alignment_record.json")
KG5_RECORD = Path("docs/roadmap/knowledge_graph/kg_005_graph_grounded_lesson_assessment_generation_record.json")
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
    "tutor_runtime_authority_authorised",
    "study_plan_runtime_authority_authorised",
    "gamification_runtime_authority_authorised",
    "parent_portal_runtime_authority_authorised",
    "llm_provider_call_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
]
REQUIRED_TRUE_KEYS = [
    "product_alignment_recorded",
    "kg5_graph_grounded_generation_valid",
    "generation_pack_dependency_recorded",
    "product_alignment_pack_artifact_generated",
    "synthetic_learner_fixture_only",
    "no_live_learner_data_used",
    "no_guardian_pii_used",
    "all_tutor_previews_reference_lessons",
    "all_tutor_previews_source_grounded",
    "all_study_plan_items_reference_lessons",
    "all_study_plan_items_source_grounded",
    "all_gamification_candidates_reference_assessments",
    "all_gamification_candidates_source_grounded",
    "all_parent_summaries_synthetic_only",
    "all_parent_summaries_source_grounded",
    "all_product_edges_source_grounded",
    "all_product_items_review_required",
    "all_product_items_advisory_only",
    "duplicate_tutor_preview_keys_found_false",
    "duplicate_study_plan_item_keys_found_false",
    "duplicate_award_candidate_keys_found_false",
    "duplicate_parent_summary_keys_found_false",
    "orphan_product_edges_found_false",
    "product_review_boundary_recorded",
    "parent_privacy_boundary_recorded",
    "runtime_kg_boundary_recorded",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    record = read_json(root / RECORD)
    kg5 = read_json(root / KG5_RECORD)
    audit_result = audit(root)
    errors: list[str] = []
    warnings: list[str] = []

    kg5_valid = kg5.get("graph_grounded_generation_recorded") is True and kg5.get("kg_id") == "KG-5"
    if not kg5_valid:
        errors.append("KG-5 graph-grounded generation must be recorded before KG-6")
    if record.get("kg_id") != KG_ID:
        errors.append("KG-6 record must have kg_id KG-6")
    if not audit_result.get("authority_valid"):
        errors.extend([f"authority audit failed: {err}" for err in audit_result.get("errors", [])])

    captured = record.get("product_alignment_recorded") is True
    if captured:
        if not audit_result.get("final_valid"):
            errors.extend([f"final KG-6 product alignment evidence failed: {err}" for err in audit_result.get("errors", [])])
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
        if int(record.get("tutor_preview_count") or 0) < 200:
            errors.append("KG-6 tutor preview count must be at least 200")
        if int(record.get("study_plan_item_count") or 0) < 200:
            errors.append("KG-6 study plan item count must be at least 200")
        if int(record.get("gamification_award_candidate_count") or 0) < 200:
            errors.append("KG-6 gamification candidate count must be at least 200")
    else:
        warnings.append("KG-6 record is still pending evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    authority_errors = [
        e for e in errors
        if not e.startswith("record flag must be true")
        and not e.startswith("final KG-6 product alignment evidence failed")
        and "count must be at least" not in e
    ]
    authority_valid = not authority_errors and audit_result.get("authority_valid") is True and kg5_valid
    valid = authority_valid and captured and not errors

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "kg_id": KG_ID,
        "record_path": str(RECORD),
        "errors": errors,
        "warnings": warnings,
        "kg5_graph_grounded_generation_valid": kg5_valid,
        "product_alignment_recorded": captured,
        "generation_pack_dependency_recorded": record.get("generation_pack_dependency_recorded") is True,
        "product_alignment_pack_artifact_generated": record.get("product_alignment_pack_artifact_generated") is True,
        "synthetic_learner_fixture_only": record.get("synthetic_learner_fixture_only") is True,
        "no_live_learner_data_used": record.get("no_live_learner_data_used") is True,
        "no_guardian_pii_used": record.get("no_guardian_pii_used") is True,
        "tutor_preview_count": int(record.get("tutor_preview_count") or 0),
        "study_plan_item_count": int(record.get("study_plan_item_count") or 0),
        "gamification_award_candidate_count": int(record.get("gamification_award_candidate_count") or 0),
        "parent_alignment_summary_count": int(record.get("parent_alignment_summary_count") or 0),
        "product_alignment_edge_count": int(record.get("product_alignment_edge_count") or 0),
        "all_tutor_previews_reference_lessons": record.get("all_tutor_previews_reference_lessons") is True,
        "all_tutor_previews_source_grounded": record.get("all_tutor_previews_source_grounded") is True,
        "all_study_plan_items_reference_lessons": record.get("all_study_plan_items_reference_lessons") is True,
        "all_study_plan_items_source_grounded": record.get("all_study_plan_items_source_grounded") is True,
        "all_gamification_candidates_reference_assessments": record.get("all_gamification_candidates_reference_assessments") is True,
        "all_gamification_candidates_source_grounded": record.get("all_gamification_candidates_source_grounded") is True,
        "all_parent_summaries_synthetic_only": record.get("all_parent_summaries_synthetic_only") is True,
        "all_parent_summaries_source_grounded": record.get("all_parent_summaries_source_grounded") is True,
        "all_product_edges_source_grounded": record.get("all_product_edges_source_grounded") is True,
        "all_product_items_review_required": record.get("all_product_items_review_required") is True,
        "all_product_items_advisory_only": record.get("all_product_items_advisory_only") is True,
        "duplicate_tutor_preview_keys_found_false": record.get("duplicate_tutor_preview_keys_found_false") is True,
        "duplicate_study_plan_item_keys_found_false": record.get("duplicate_study_plan_item_keys_found_false") is True,
        "duplicate_award_candidate_keys_found_false": record.get("duplicate_award_candidate_keys_found_false") is True,
        "duplicate_parent_summary_keys_found_false": record.get("duplicate_parent_summary_keys_found_false") is True,
        "orphan_product_edges_found_false": record.get("orphan_product_edges_found_false") is True,
        "product_review_boundary_recorded": record.get("product_review_boundary_recorded") is True,
        "parent_privacy_boundary_recorded": record.get("parent_privacy_boundary_recorded") is True,
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
        print(f"KG-6 product alignment valid: {result['valid']}")
        print(f"KG-6 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
