#!/usr/bin/env python3
"""Verify KG-8 post-switch optimisation and scale review evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.knowledge_graph.audit_kg008_post_switch_optimisation_scale_review import audit

KG_ID = "KG-8"
RECORD = Path("docs/roadmap/knowledge_graph/kg_008_post_switch_optimisation_scale_review_record.json")
KGACT001_RECORD = Path("docs/roadmap/knowledge_graph/kg_act_001_controlled_runtime_kg_authority_activation_record.json")

REQUIRED_TRUE_KEYS = [
    "post_switch_optimisation_scale_review_recorded",
    "kgact001_controlled_runtime_activation_valid",
    "post_switch_review_pack_artifact_generated",
    "post_switch_go_no_go_review_approved",
    "optimisation_backlog_reviewed",
    "scale_review_completed",
    "monitoring_observability_review_completed",
    "rollback_observability_review_completed",
    "popia_post_switch_boundary_reviewed",
    "post_switch_boundary_recorded",
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "authority_switch_executed",
    "all_optimisation_candidates_source_grounded",
    "all_scale_review_checks_source_grounded",
    "all_monitoring_requirements_source_grounded",
    "all_rollback_observability_checks_source_grounded",
    "all_post_switch_edges_source_grounded",
    "all_post_switch_items_review_only",
    "duplicate_post_switch_item_keys_found_false",
    "orphan_post_switch_edges_found_false",
    "kg_roadmap_completed_through_kg8",
]

BOUNDARY_FALSE_KEYS = [
    "database_schema_migration_authorised",
    "learner_facing_model_change_authorised",
    "learner_graph_persistence_authorised",
    "legacy_cleanup_executed",
    "llm_provider_call_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "optimisation_execution_authorised",
    "scale_load_test_execution_authorised",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    record = read_json(root / RECORD)
    kgact001 = read_json(root / KGACT001_RECORD)
    audit_result = audit(root)
    errors: list[str] = []
    warnings: list[str] = []

    kgact001_valid = (
        kgact001.get("kg_id") == "KG-ACT-001"
        and kgact001.get("controlled_runtime_kg_authority_activation_recorded") is True
        and kgact001.get("runtime_kg_authority_switch_authorised") is True
        and kgact001.get("authority_switch_executed") is True
        and kgact001.get("kg8_post_switch_optimisation_unblocked") is True
    )
    if not kgact001_valid:
        errors.append("KG-8 requires valid KG-ACT-001 controlled runtime KG activation evidence")
    if record.get("kg_id") != KG_ID:
        errors.append("KG-8 record must have kg_id KG-8")
    if not audit_result.get("authority_valid"):
        errors.extend([f"authority audit failed: {err}" for err in audit_result.get("errors", [])])

    captured = record.get("post_switch_optimisation_scale_review_recorded") is True
    if captured:
        if not audit_result.get("final_valid"):
            errors.extend([f"final KG-8 evidence failed: {err}" for err in audit_result.get("errors", [])])
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
        if int(record.get("optimisation_candidate_count") or 0) < 8:
            errors.append("KG-8 optimisation candidate count must be at least 8")
        if int(record.get("scale_review_check_count") or 0) < 10:
            errors.append("KG-8 scale review check count must be at least 10")
        if int(record.get("monitoring_requirement_count") or 0) < 8:
            errors.append("KG-8 monitoring requirement count must be at least 8")
        if int(record.get("rollback_observability_check_count") or 0) < 6:
            errors.append("KG-8 rollback observability count must be at least 6")
    else:
        warnings.append("KG-8 record is still pending post-switch review evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    authority_errors = [
        error for error in errors
        if not error.startswith("record flag must be true")
        and not error.startswith("final KG-8 evidence failed")
        and "count must" not in error
    ]
    authority_valid = not authority_errors and audit_result.get("authority_valid") is True and kgact001_valid
    valid = authority_valid and captured and not errors
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "kg_id": KG_ID,
        "record_path": str(RECORD),
        "errors": errors,
        "warnings": warnings,
        "kgact001_controlled_runtime_activation_valid": kgact001_valid,
        "post_switch_optimisation_scale_review_recorded": captured,
        "post_switch_review_pack_artifact_generated": record.get("post_switch_review_pack_artifact_generated") is True,
        "post_switch_go_no_go_review_approved": record.get("post_switch_go_no_go_review_approved") is True,
        "optimisation_backlog_reviewed": record.get("optimisation_backlog_reviewed") is True,
        "scale_review_completed": record.get("scale_review_completed") is True,
        "monitoring_observability_review_completed": record.get("monitoring_observability_review_completed") is True,
        "rollback_observability_review_completed": record.get("rollback_observability_review_completed") is True,
        "popia_post_switch_boundary_reviewed": record.get("popia_post_switch_boundary_reviewed") is True,
        "post_switch_boundary_recorded": record.get("post_switch_boundary_recorded") is True,
        "optimisation_candidate_count": int(record.get("optimisation_candidate_count") or 0),
        "scale_review_check_count": int(record.get("scale_review_check_count") or 0),
        "monitoring_requirement_count": int(record.get("monitoring_requirement_count") or 0),
        "rollback_observability_check_count": int(record.get("rollback_observability_check_count") or 0),
        "post_switch_review_edge_count": int(record.get("post_switch_review_edge_count") or 0),
        "readiness_check_count_inherited": int(record.get("readiness_check_count_inherited") or 0),
        "legacy_projection_mapping_count_inherited": int(record.get("legacy_projection_mapping_count_inherited") or 0),
        "rollback_control_count_inherited": int(record.get("rollback_control_count_inherited") or 0),
        "all_optimisation_candidates_source_grounded": record.get("all_optimisation_candidates_source_grounded") is True,
        "all_scale_review_checks_source_grounded": record.get("all_scale_review_checks_source_grounded") is True,
        "all_monitoring_requirements_source_grounded": record.get("all_monitoring_requirements_source_grounded") is True,
        "all_rollback_observability_checks_source_grounded": record.get("all_rollback_observability_checks_source_grounded") is True,
        "all_post_switch_edges_source_grounded": record.get("all_post_switch_edges_source_grounded") is True,
        "all_post_switch_items_review_only": record.get("all_post_switch_items_review_only") is True,
        "duplicate_post_switch_item_keys_found_false": record.get("duplicate_post_switch_item_keys_found_false") is True,
        "orphan_post_switch_edges_found_false": record.get("orphan_post_switch_edges_found_false") is True,
        "kg_roadmap_completed_through_kg8": record.get("kg_roadmap_completed_through_kg8") is True,
        "audit": audit_result,
        **{key: record.get(key) for key in [
            "runtime_kg_implementation_claimed",
            "runtime_kg_authority_switch_authorised",
            "authority_switch_executed",
            *BOUNDARY_FALSE_KEYS,
        ]},
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
        print(f"KG-8 post-switch optimisation/scale review valid: {result['valid']}")
        print(f"KG-8 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
