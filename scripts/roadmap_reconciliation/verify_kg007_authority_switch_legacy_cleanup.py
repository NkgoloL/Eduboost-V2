#!/usr/bin/env python3
"""Verify KG-7 authority-switch readiness and legacy-cleanup evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.knowledge_graph.audit_kg007_authority_switch_legacy_cleanup import audit

KG_ID = "KG-7"
RECORD = Path("docs/roadmap/knowledge_graph/kg_007_authority_switch_legacy_cleanup_record.json")
KG6_RECORD = Path("docs/roadmap/knowledge_graph/kg_006_tutor_study_plan_gamification_parent_alignment_record.json")
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
    "authority_switch_executed",
    "legacy_cleanup_executed",
    "llm_provider_call_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
]
REQUIRED_TRUE_KEYS = [
    "authority_switch_legacy_cleanup_recorded",
    "kg6_product_alignment_valid",
    "product_alignment_dependency_recorded",
    "authority_switch_readiness_pack_artifact_generated",
    "synthetic_learner_fixture_only",
    "no_live_learner_data_used",
    "no_guardian_pii_used",
    "all_authority_readiness_checks_passed",
    "all_legacy_projection_mappings_source_grounded",
    "all_readiness_checks_source_grounded",
    "all_cleanup_tasks_source_grounded",
    "all_rollback_controls_source_grounded",
    "all_switch_edges_source_grounded",
    "all_legacy_projection_mappings_readiness_only",
    "all_cleanup_tasks_planned_not_executed",
    "all_rollback_controls_available",
    "duplicate_readiness_check_keys_found_false",
    "duplicate_legacy_projection_keys_found_false",
    "duplicate_cleanup_task_keys_found_false",
    "duplicate_rollback_control_keys_found_false",
    "orphan_switch_edges_found_false",
    "feature_flag_boundary_recorded",
    "legacy_cleanup_boundary_recorded",
    "rollback_boundary_recorded",
    "runtime_kg_boundary_recorded",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    record = read_json(root / RECORD)
    kg6 = read_json(root / KG6_RECORD)
    audit_result = audit(root)
    errors: list[str] = []
    warnings: list[str] = []

    kg6_valid = kg6.get("product_alignment_recorded") is True and kg6.get("kg_id") == "KG-6"
    if not kg6_valid:
        errors.append("KG-6 product alignment must be recorded before KG-7")
    if record.get("kg_id") != KG_ID:
        errors.append("KG-7 record must have kg_id KG-7")
    if not audit_result.get("authority_valid"):
        errors.extend([f"authority audit failed: {err}" for err in audit_result.get("errors", [])])

    captured = record.get("authority_switch_legacy_cleanup_recorded") is True
    if captured:
        if not audit_result.get("final_valid"):
            errors.extend([f"final KG-7 authority-switch readiness evidence failed: {err}" for err in audit_result.get("errors", [])])
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
        if int(record.get("legacy_projection_mapping_count") or 0) < 700:
            errors.append("KG-7 legacy projection mapping count must be at least 700")
        if int(record.get("authority_readiness_check_count") or 0) < 10:
            errors.append("KG-7 readiness check count must be at least 10")
    else:
        warnings.append("KG-7 record is still pending evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    authority_errors = [
        e for e in errors
        if not e.startswith("record flag must be true")
        and not e.startswith("final KG-7 authority-switch readiness evidence failed")
        and "count must be at least" not in e
    ]
    authority_valid = not authority_errors and audit_result.get("authority_valid") is True and kg6_valid
    valid = authority_valid and captured and not errors

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "kg_id": KG_ID,
        "record_path": str(RECORD),
        "errors": errors,
        "warnings": warnings,
        "kg6_product_alignment_valid": kg6_valid,
        "authority_switch_legacy_cleanup_recorded": captured,
        "product_alignment_dependency_recorded": record.get("product_alignment_dependency_recorded") is True,
        "authority_switch_readiness_pack_artifact_generated": record.get("authority_switch_readiness_pack_artifact_generated") is True,
        "synthetic_learner_fixture_only": record.get("synthetic_learner_fixture_only") is True,
        "no_live_learner_data_used": record.get("no_live_learner_data_used") is True,
        "no_guardian_pii_used": record.get("no_guardian_pii_used") is True,
        "feature_flag_control_count": int(record.get("feature_flag_control_count") or 0),
        "authority_readiness_check_count": int(record.get("authority_readiness_check_count") or 0),
        "legacy_projection_mapping_count": int(record.get("legacy_projection_mapping_count") or 0),
        "legacy_cleanup_task_count": int(record.get("legacy_cleanup_task_count") or 0),
        "rollback_control_count": int(record.get("rollback_control_count") or 0),
        "switch_control_edge_count": int(record.get("switch_control_edge_count") or 0),
        "all_authority_readiness_checks_passed": record.get("all_authority_readiness_checks_passed") is True,
        "all_legacy_projection_mappings_source_grounded": record.get("all_legacy_projection_mappings_source_grounded") is True,
        "all_readiness_checks_source_grounded": record.get("all_readiness_checks_source_grounded") is True,
        "all_cleanup_tasks_source_grounded": record.get("all_cleanup_tasks_source_grounded") is True,
        "all_rollback_controls_source_grounded": record.get("all_rollback_controls_source_grounded") is True,
        "all_switch_edges_source_grounded": record.get("all_switch_edges_source_grounded") is True,
        "all_legacy_projection_mappings_readiness_only": record.get("all_legacy_projection_mappings_readiness_only") is True,
        "all_cleanup_tasks_planned_not_executed": record.get("all_cleanup_tasks_planned_not_executed") is True,
        "all_rollback_controls_available": record.get("all_rollback_controls_available") is True,
        "duplicate_readiness_check_keys_found_false": record.get("duplicate_readiness_check_keys_found_false") is True,
        "duplicate_legacy_projection_keys_found_false": record.get("duplicate_legacy_projection_keys_found_false") is True,
        "duplicate_cleanup_task_keys_found_false": record.get("duplicate_cleanup_task_keys_found_false") is True,
        "duplicate_rollback_control_keys_found_false": record.get("duplicate_rollback_control_keys_found_false") is True,
        "orphan_switch_edges_found_false": record.get("orphan_switch_edges_found_false") is True,
        "feature_flag_boundary_recorded": record.get("feature_flag_boundary_recorded") is True,
        "legacy_cleanup_boundary_recorded": record.get("legacy_cleanup_boundary_recorded") is True,
        "rollback_boundary_recorded": record.get("rollback_boundary_recorded") is True,
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
        print(f"KG-7 authority-switch readiness valid: {result['valid']}")
        print(f"KG-7 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
