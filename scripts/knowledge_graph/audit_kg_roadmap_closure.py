#!/usr/bin/env python3
"""Audit KG roadmap closure records and boundaries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

KG_CLOSURE_ID = "KG-ROADMAP-CLOSURE"
CLOSURE_RECORD = Path("docs/roadmap/knowledge_graph/kg_roadmap_closure_record.json")
CLOSURE_REPORT = Path("docs/roadmap/knowledge_graph/kg_roadmap_closure_report.md")
CLOSURE_MATRIX = Path("docs/roadmap/knowledge_graph/kg_roadmap_closure_matrix.json")
KG8_RECORD = Path("docs/roadmap/knowledge_graph/kg_008_post_switch_optimisation_scale_review_record.json")

KG_RECORDS: list[dict[str, str]] = [
    {"kg_id": "KG-0", "path": "docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval_record.json", "completion_flag": "formal_kg_roadmap_approval_recorded"},
    {"kg_id": "KG-1", "path": "docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation_record.json", "completion_flag": "caps_graph_foundation_recorded"},
    {"kg_id": "KG-2", "path": "docs/roadmap/knowledge_graph/kg_002_target_graph_generation_record.json", "completion_flag": "target_graph_generation_recorded"},
    {"kg_id": "KG-3", "path": "docs/roadmap/knowledge_graph/kg_003_learner_graph_shadow_mode_record.json", "completion_flag": "learner_graph_shadow_mode_recorded"},
    {"kg_id": "KG-4", "path": "docs/roadmap/knowledge_graph/kg_004_gap_engine_intervention_planner_record.json", "completion_flag": "gap_engine_intervention_planner_recorded"},
    {"kg_id": "KG-5", "path": "docs/roadmap/knowledge_graph/kg_005_graph_grounded_lesson_assessment_generation_record.json", "completion_flag": "graph_grounded_generation_recorded"},
    {"kg_id": "KG-6", "path": "docs/roadmap/knowledge_graph/kg_006_tutor_study_plan_gamification_parent_alignment_record.json", "completion_flag": "product_alignment_recorded"},
    {"kg_id": "KG-7", "path": "docs/roadmap/knowledge_graph/kg_007_authority_switch_legacy_cleanup_record.json", "completion_flag": "authority_switch_legacy_cleanup_recorded"},
    {"kg_id": "KG-ACT-001", "path": "docs/roadmap/knowledge_graph/kg_act_001_controlled_runtime_kg_authority_activation_record.json", "completion_flag": "controlled_runtime_kg_authority_activation_recorded"},
    {"kg_id": "KG-8", "path": "docs/roadmap/knowledge_graph/kg_008_post_switch_optimisation_scale_review_record.json", "completion_flag": "post_switch_optimisation_scale_review_recorded"},
]

BOUNDARY_FALSE_KEYS = [
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]

KG8_FALSE_KEYS = [
    "database_schema_migration_authorised",
    "learner_facing_model_change_authorised",
    "learner_graph_persistence_authorised",
    "legacy_cleanup_executed",
    "llm_provider_call_authorised",
    "optimisation_execution_authorised",
    "scale_load_test_execution_authorised",
    *BOUNDARY_FALSE_KEYS,
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def matrix_status(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in KG_RECORDS:
        path = root / spec["path"]
        record = read_json(path)
        rows.append({
            "kg_id": spec["kg_id"],
            "record_path": spec["path"],
            "record_present": path.exists(),
            "recorded": record.get(spec["completion_flag"]) is True,
            "completion_flag": spec["completion_flag"],
            "status": record.get("status"),
            "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed"),
            "runtime_kg_authority_switch_authorised": record.get("runtime_kg_authority_switch_authorised"),
            "authority_switch_executed": record.get("authority_switch_executed"),
            "production_release_authorised": record.get("production_release_authorised"),
            "deployment_authorised": record.get("deployment_authorised"),
            "public_beta_authorised": record.get("public_beta_authorised"),
            "billing_launch_authorised": record.get("billing_launch_authorised"),
        })
    return rows


def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    missing_authority_files = [
        str(path) for path in [CLOSURE_REPORT, CLOSURE_MATRIX, CLOSURE_RECORD]
        if not (root / path).exists()
    ]
    if missing_authority_files:
        errors.extend(f"missing closure authority file: {path}" for path in missing_authority_files)

    rows = matrix_status(root)
    missing_records = [row["kg_id"] for row in rows if not row["record_present"]]
    incomplete_records = [row["kg_id"] for row in rows if row["record_present"] and not row["recorded"]]
    if missing_records:
        errors.append("missing KG records: " + ", ".join(missing_records))
    if incomplete_records:
        errors.append("incomplete KG records: " + ", ".join(incomplete_records))

    kg8 = read_json(root / KG8_RECORD)
    if kg8.get("kg_id") != "KG-8":
        errors.append("KG-8 record must be present and identify kg_id KG-8")
    if kg8.get("kg_roadmap_completed_through_kg8") is not True:
        errors.append("KG-8 must record kg_roadmap_completed_through_kg8 true")
    if kg8.get("runtime_kg_implementation_claimed") is not True:
        errors.append("KG-8 must inherit runtime_kg_implementation_claimed true from KG-ACT-001")
    if kg8.get("runtime_kg_authority_switch_authorised") is not True:
        errors.append("KG-8 must inherit runtime_kg_authority_switch_authorised true from KG-ACT-001")
    if kg8.get("authority_switch_executed") is not True:
        errors.append("KG-8 must inherit authority_switch_executed true from KG-ACT-001")
    for key in KG8_FALSE_KEYS:
        if kg8.get(key) is not False:
            errors.append(f"KG-8 boundary flag must remain false: {key}")

    matrix = read_json(root / CLOSURE_MATRIX)
    if matrix:
        if matrix.get("closure_id") != KG_CLOSURE_ID:
            errors.append("closure matrix must identify KG-ROADMAP-CLOSURE")
        matrix_ids = [row.get("kg_id") for row in matrix.get("kg_items", [])]
        expected_ids = [spec["kg_id"] for spec in KG_RECORDS]
        if matrix_ids != expected_ids:
            errors.append("closure matrix KG item order must match KG-0..KG-8 with KG-ACT-001 before KG-8")
        if matrix.get("kg008_non_required_check_pytest_path_caveat_visible") is not True:
            errors.append("closure matrix must preserve the KG-8 non-required pytest/PATH caveat")

    record = read_json(root / CLOSURE_RECORD)
    captured = record.get("kg_roadmap_closure_recorded") is True
    if captured:
        for key in [
            "all_kg_items_closed_through_kg8",
            "kgact001_activation_gate_closed",
            "kg8_post_switch_review_closed",
            "kg008_non_required_check_pytest_path_caveat_visible",
            "kg_roadmap_closed_no_new_kg_slice_authorised",
        ]:
            if record.get(key) is not True:
                errors.append(f"closure record flag must be true: {key}")
        if record.get("kg_item_count") != len(KG_RECORDS):
            errors.append(f"closure record kg_item_count must be {len(KG_RECORDS)}")
        if record.get("runtime_kg_implementation_claimed") is not True:
            errors.append("closure record must preserve runtime KG implementation claimed true")
        if record.get("runtime_kg_authority_switch_authorised") is not True:
            errors.append("closure record must preserve runtime KG authority switch authorised true")
        if record.get("authority_switch_executed") is not True:
            errors.append("closure record must preserve authority switch executed true")
        for key in BOUNDARY_FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"closure boundary flag must remain false: {key}")
    else:
        warnings.append("KG roadmap closure record is pending evidence capture")

    final_valid = captured and not errors
    return {
        "authority_valid": not errors or (not captured and not [e for e in errors if "closure record flag" not in e]),
        "final_valid": final_valid,
        "closure_recorded": captured,
        "errors": errors,
        "warnings": warnings,
        "missing_records": missing_records,
        "incomplete_records": incomplete_records,
        "kg_item_count": len(KG_RECORDS),
        "kg_items": rows,
        "kg8_counts": {
            "optimisation_candidate_count": int(kg8.get("optimisation_candidate_count") or 0),
            "scale_review_check_count": int(kg8.get("scale_review_check_count") or 0),
            "monitoring_requirement_count": int(kg8.get("monitoring_requirement_count") or 0),
            "rollback_observability_check_count": int(kg8.get("rollback_observability_check_count") or 0),
            "post_switch_review_edge_count": int(kg8.get("post_switch_review_edge_count") or 0),
        },
        "kg008_non_required_check_pytest_path_caveat_visible": (matrix.get("kg008_non_required_check_pytest_path_caveat_visible") is True) if matrix else False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"KG roadmap closure authority valid: {result['authority_valid']}")
        print(f"KG roadmap closure final valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["authority_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
