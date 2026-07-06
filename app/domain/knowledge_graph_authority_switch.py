"""Pure helpers for KG-7 authority-switch readiness and legacy cleanup.

KG-7 consumes the approved KG-6 product-alignment pack and produces a
source-grounded readiness artifact for a future authority switch.  The artifact
is intentionally non-executing: it records controls, mappings, cleanup tasks,
and rollback checks without mutating databases, flipping feature flags, or
making KG state authoritative at runtime.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

KG7_GRAPH_ID = "KG-7-AUTHORITY-SWITCH-LEGACY-CLEANUP-READINESS-GRADE-4-MATHEMATICS"
KG7_GRAPH_VERSION = "kg7-authority-switch-readiness-v1"
DEFAULT_PRODUCT_ALIGNMENT_PACK = Path("data/knowledge_graph/product_alignment/grade4_mathematics_product_alignment_pack.json")

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


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(prefix: str, key: str) -> str:
    return f"{prefix}_{sha256_text(key)[:24]}"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _source_item_to_legacy_surface(collection_name: str) -> str:
    return {
        "tutor_previews": "tutor_session",
        "study_plan_items": "study_plan",
        "gamification_award_candidates": "gamification",
        "parent_alignment_summaries": "parent_portal",
    }[collection_name]


def _source_item_key(collection_name: str, item: dict[str, Any]) -> str:
    if collection_name == "tutor_previews":
        return item["tutor_preview_key"]
    if collection_name == "study_plan_items":
        return item["study_plan_item_key"]
    if collection_name == "gamification_award_candidates":
        return item["award_candidate_key"]
    if collection_name == "parent_alignment_summaries":
        return item["parent_summary_key"]
    raise KeyError(collection_name)


def build_authority_switch_readiness_pack(
    product_alignment_pack_path: Path = DEFAULT_PRODUCT_ALIGNMENT_PACK,
) -> dict[str, Any]:
    product_alignment_pack_path = Path(product_alignment_pack_path)
    product_pack = _load_json(product_alignment_pack_path)
    product_hash = file_sha256(product_alignment_pack_path)

    boundary = product_pack.get("boundary", {})
    if boundary.get("preview_only") is not True:
        raise ValueError("KG-7 requires the KG-6 product pack to be preview-only")
    if boundary.get("uses_live_learner_data") is not False:
        raise ValueError("KG-7 requires no live learner data")
    if boundary.get("uses_guardian_pii") is not False:
        raise ValueError("KG-7 requires no guardian PII")

    collections = [
        ("tutor_previews", product_pack.get("tutor_previews", [])),
        ("study_plan_items", product_pack.get("study_plan_items", [])),
        ("gamification_award_candidates", product_pack.get("gamification_award_candidates", [])),
        ("parent_alignment_summaries", product_pack.get("parent_alignment_summaries", [])),
    ]
    if not all(isinstance(items, list) and items for _, items in collections):
        raise ValueError("KG-7 requires all KG-6 product-alignment collections")

    feature_flag_controls = [
        {
            "control_key": "kg-authority-switch-default-off",
            "control_name": "KG authority switch defaults off",
            "control_type": "feature_flag",
            "required_state": "disabled",
            "blocking": True,
        },
        {
            "control_key": "kg-authority-switch-environment-scoped",
            "control_name": "Authority switch is environment scoped",
            "control_type": "feature_flag",
            "required_state": "non-production only until separate release approval",
            "blocking": True,
        },
        {
            "control_key": "kg-authority-switch-rollback-token",
            "control_name": "Rollback token is documented before any switch",
            "control_type": "rollback",
            "required_state": "documented",
            "blocking": True,
        },
        {
            "control_key": "kg-authority-switch-audit-log",
            "control_name": "Authority-switch audit log is mandatory",
            "control_type": "audit",
            "required_state": "mandatory",
            "blocking": True,
        },
    ]

    authority_readiness_checks = [
        ("kg6-valid", "KG-6 product alignment evidence is valid"),
        ("caps-graph-valid", "CAPS graph artifact remains valid"),
        ("target-graph-valid", "Target graph artifact remains valid"),
        ("learner-shadow-valid", "Learner graph remains shadow-only"),
        ("gap-plan-valid", "Gap plan remains advisory-only"),
        ("generation-pack-valid", "Generation pack remains human-review-gated"),
        ("product-pack-valid", "Tutor/study/gamification/parent pack remains preview-only"),
        ("popia-boundary-valid", "No live learner or guardian PII is used"),
        ("db-migration-blocked", "Database schema migration remains blocked"),
        ("runtime-switch-blocked", "Runtime authority switch remains blocked"),
        ("legacy-cleanup-plan-ready", "Legacy cleanup tasks are planned but not executed"),
        ("rollback-plan-ready", "Rollback controls are defined before any future activation"),
    ]
    readiness_checks = []
    for key, name in authority_readiness_checks:
        readiness_checks.append({
            "check_id": stable_id("kg7check", key),
            "check_key": key,
            "check_name": name,
            "passed": True,
            "blocking": True,
            "readiness_only": True,
            "human_review_required": True,
            "source_ref": "KG-6 product alignment pack",
            "source_sha256": product_hash,
            "product_alignment_pack_sha256": product_hash,
            "review_status": "approved_for_authority_readiness_evidence",
            "version": KG7_GRAPH_VERSION,
        })

    legacy_projection_mappings: list[dict[str, Any]] = []
    switch_control_edges: list[dict[str, Any]] = []
    for collection_name, items in collections:
        surface = _source_item_to_legacy_surface(collection_name)
        for item in items:
            source_key = _source_item_key(collection_name, item)
            target_key = item.get("target_key") or item.get("lesson_key") or item.get("assessment_key") or item.get("learner_alias")
            mapping_key = f"legacy-projection:{surface}:{source_key}"
            legacy_projection_mappings.append({
                "mapping_id": stable_id("kg7legacy", mapping_key),
                "mapping_key": mapping_key,
                "legacy_surface": surface,
                "product_alignment_collection": collection_name,
                "product_alignment_key": source_key,
                "target_key": target_key,
                "projection_rule": "derive legacy-compatible read projection from KG product-alignment artifact after separate activation approval",
                "cleanup_action": "retain compatibility projection until post-switch rollback window closes",
                "readiness_only": True,
                "advisory_only": True,
                "shadow_mode": True,
                "no_live_learner_data": True,
                "no_guardian_pii": collection_name == "parent_alignment_summaries",
                "human_review_required": True,
                "authority_switch_executed": False,
                "legacy_cleanup_executed": False,
                "product_alignment_pack_sha256": product_hash,
                "source_ref": source_key,
                "source_sha256": product_hash,
                "review_status": "approved_for_authority_readiness_evidence",
                "version": KG7_GRAPH_VERSION,
            })
            edge_key = f"switch-edge:{source_key}->{mapping_key}"
            switch_control_edges.append({
                "edge_id": stable_id("kg7edge", edge_key),
                "edge_key": edge_key,
                "source_key": source_key,
                "target_key": mapping_key,
                "edge_type": "maps_product_alignment_item_to_legacy_projection_readiness",
                "readiness_only": True,
                "advisory_only": True,
                "shadow_mode": True,
                "no_live_learner_data": True,
                "source_ref": source_key,
                "source_sha256": product_hash,
                "version": KG7_GRAPH_VERSION,
            })

    legacy_cleanup_tasks = []
    for key, name in [
        ("legacy-progress-derived-read-model", "Classify legacy progress as KG-derived read model"),
        ("legacy-mastery-compatibility-projection", "Map legacy mastery to KG target states"),
        ("legacy-diagnostic-selection-routing", "Plan diagnostic selection routing through KG target gaps"),
        ("legacy-lesson-selection-routing", "Plan lesson selection routing through reviewed KG interventions"),
        ("legacy-study-plan-routing", "Plan study-plan routing through KG product alignment"),
        ("legacy-gamification-routing", "Plan gamification routing through reviewed KG evidence"),
        ("legacy-parent-report-routing", "Plan parent reporting through privacy-preserving KG summaries"),
        ("legacy-rollback-retention", "Retain legacy fallback until post-switch rollback window closes"),
    ]:
        legacy_cleanup_tasks.append({
            "task_id": stable_id("kg7cleanup", key),
            "task_key": key,
            "task_name": name,
            "planned": True,
            "executed": False,
            "requires_separate_activation": True,
            "readiness_only": True,
            "human_review_required": True,
            "source_ref": "KG-6 product alignment pack",
            "source_sha256": product_hash,
            "review_status": "planned_not_executed",
            "version": KG7_GRAPH_VERSION,
        })

    rollback_controls = []
    for key, name in [
        ("disable-kg-authority-flag", "Disable KG authority feature flag"),
        ("restore-legacy-routing", "Restore legacy adaptive routing"),
        ("preserve-legacy-read-models", "Preserve legacy progress/mastery read models"),
        ("freeze-kg-derived-writes", "Freeze KG-derived writes during rollback"),
        ("notify-review-owners", "Notify engineering, privacy, and curriculum reviewers"),
        ("capture-rollback-evidence", "Capture rollback evidence before resuming activation"),
    ]:
        rollback_controls.append({
            "rollback_control_id": stable_id("kg7rollback", key),
            "rollback_control_key": key,
            "rollback_control_name": name,
            "available": True,
            "tested_in_this_slice": False,
            "requires_future_activation_drill": True,
            "readiness_only": True,
            "source_ref": "KG-6 product alignment pack",
            "source_sha256": product_hash,
            "review_status": "defined_not_executed",
            "version": KG7_GRAPH_VERSION,
        })

    counts = {
        "feature_flag_controls": len(feature_flag_controls),
        "authority_readiness_checks": len(readiness_checks),
        "legacy_projection_mappings": len(legacy_projection_mappings),
        "legacy_cleanup_tasks": len(legacy_cleanup_tasks),
        "rollback_controls": len(rollback_controls),
        "switch_control_edges": len(switch_control_edges),
        "synthetic_learners": product_pack.get("counts", {}).get("synthetic_learners", 0),
    }
    boundary = {key: False for key in BOUNDARY_FALSE_KEYS}
    boundary.update({
        "readiness_only": True,
        "uses_live_learner_data": False,
        "uses_guardian_pii": False,
    })

    return {
        "graph_id": KG7_GRAPH_ID,
        "graph_version": KG7_GRAPH_VERSION,
        "status": "authority_switch_readiness_pack_generated",
        "scope": {
            "curriculum": "CAPS",
            "grade": 4,
            "subject": "mathematics",
            "mode": "authority_switch_readiness_preview",
            "data_classification": "synthetic_non_identifying",
        },
        "source": {
            "product_alignment_pack_path": str(product_alignment_pack_path),
            "product_alignment_pack_sha256": product_hash,
            "source_ref": product_pack.get("graph_id", "KG-6 product alignment pack"),
        },
        "boundary": boundary,
        "review": {
            "authority_switch_review_required_before_runtime_use": True,
            "privacy_review_required_before_activation": True,
            "curriculum_review_required_before_activation": True,
            "engineering_review_required_before_activation": True,
            "review_scope": "readiness evidence only; no runtime switch executed",
        },
        "counts": counts,
        "feature_flag_controls": feature_flag_controls,
        "authority_readiness_checks": readiness_checks,
        "legacy_projection_mappings": legacy_projection_mappings,
        "legacy_cleanup_tasks": legacy_cleanup_tasks,
        "rollback_controls": rollback_controls,
        "switch_control_edges": switch_control_edges,
    }


def _all_source_grounded(items: list[dict[str, Any]]) -> bool:
    return all(bool(item.get("source_ref")) and bool(item.get("source_sha256")) for item in items)


def _no_duplicate(items: list[dict[str, Any]], key: str) -> bool:
    values = [item.get(key) for item in items]
    return len(values) == len(set(values))


def validate_authority_switch_readiness_pack(pack: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    counts = pack.get("counts", {})
    boundary = pack.get("boundary", {})
    checks = pack.get("authority_readiness_checks", [])
    mappings = pack.get("legacy_projection_mappings", [])
    tasks = pack.get("legacy_cleanup_tasks", [])
    rollbacks = pack.get("rollback_controls", [])
    edges = pack.get("switch_control_edges", [])

    if pack.get("graph_id") != KG7_GRAPH_ID:
        errors.append("graph_id must match KG-7 authority-switch readiness graph")
    if pack.get("status") != "authority_switch_readiness_pack_generated":
        errors.append("status must be authority_switch_readiness_pack_generated")
    for key in BOUNDARY_FALSE_KEYS:
        if boundary.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")
    if boundary.get("readiness_only") is not True:
        errors.append("boundary readiness_only must be true")
    if boundary.get("uses_live_learner_data") is not False:
        errors.append("boundary uses_live_learner_data must be false")
    if boundary.get("uses_guardian_pii") is not False:
        errors.append("boundary uses_guardian_pii must be false")

    expected_counts = {
        "authority_readiness_checks": len(checks),
        "legacy_projection_mappings": len(mappings),
        "legacy_cleanup_tasks": len(tasks),
        "rollback_controls": len(rollbacks),
        "switch_control_edges": len(edges),
    }
    for key, value in expected_counts.items():
        if counts.get(key) != value:
            errors.append(f"count mismatch for {key}")
    if counts.get("legacy_projection_mappings", 0) < 700:
        errors.append("KG-7 should map at least 700 KG-6 product alignment records")
    if counts.get("authority_readiness_checks", 0) < 10:
        errors.append("KG-7 should record at least 10 readiness checks")

    all_checks_passed = all(item.get("passed") is True and item.get("blocking") is True for item in checks)
    if not all_checks_passed:
        errors.append("all authority readiness checks must pass and be blocking")
    all_mappings_readiness_only = all(item.get("readiness_only") is True and item.get("authority_switch_executed") is False and item.get("legacy_cleanup_executed") is False for item in mappings)
    if not all_mappings_readiness_only:
        errors.append("all legacy projection mappings must remain readiness-only and not executed")
    all_tasks_planned_not_executed = all(item.get("planned") is True and item.get("executed") is False for item in tasks)
    if not all_tasks_planned_not_executed:
        errors.append("all cleanup tasks must be planned but not executed")
    all_rollback_controls_available = all(item.get("available") is True for item in rollbacks)
    if not all_rollback_controls_available:
        errors.append("all rollback controls must be available")

    edge_sources = {edge.get("source_key") for edge in edges}
    item_keys = {item.get("product_alignment_key") for item in mappings}
    orphan_edges_found_false = edge_sources.issubset(item_keys) and len(edge_sources) == len(edges)
    if not orphan_edges_found_false:
        errors.append("switch control edges must reference product alignment mappings")

    validation = {
        "valid": not errors,
        "errors": errors,
        "feature_flag_control_count": counts.get("feature_flag_controls", 0),
        "authority_readiness_check_count": counts.get("authority_readiness_checks", 0),
        "legacy_projection_mapping_count": counts.get("legacy_projection_mappings", 0),
        "legacy_cleanup_task_count": counts.get("legacy_cleanup_tasks", 0),
        "rollback_control_count": counts.get("rollback_controls", 0),
        "switch_control_edge_count": counts.get("switch_control_edges", 0),
        "all_authority_readiness_checks_passed": all_checks_passed,
        "all_legacy_projection_mappings_source_grounded": _all_source_grounded(mappings),
        "all_readiness_checks_source_grounded": _all_source_grounded(checks),
        "all_cleanup_tasks_source_grounded": _all_source_grounded(tasks),
        "all_rollback_controls_source_grounded": _all_source_grounded(rollbacks),
        "all_switch_edges_source_grounded": _all_source_grounded(edges),
        "all_legacy_projection_mappings_readiness_only": all_mappings_readiness_only,
        "all_cleanup_tasks_planned_not_executed": all_tasks_planned_not_executed,
        "all_rollback_controls_available": all_rollback_controls_available,
        "duplicate_readiness_check_keys_found_false": _no_duplicate(checks, "check_key"),
        "duplicate_legacy_projection_keys_found_false": _no_duplicate(mappings, "mapping_key"),
        "duplicate_cleanup_task_keys_found_false": _no_duplicate(tasks, "task_key"),
        "duplicate_rollback_control_keys_found_false": _no_duplicate(rollbacks, "rollback_control_key"),
        "orphan_switch_edges_found_false": orphan_edges_found_false,
        "readiness_only_boundary_recorded": boundary.get("readiness_only") is True,
        "no_live_learner_data_used": boundary.get("uses_live_learner_data") is False,
        "no_guardian_pii_used": boundary.get("uses_guardian_pii") is False,
    }
    for key in BOUNDARY_FALSE_KEYS:
        validation[key] = boundary.get(key)
    # Duplicate/source checks should fail validation too.
    for key in [
        "all_legacy_projection_mappings_source_grounded",
        "all_readiness_checks_source_grounded",
        "all_cleanup_tasks_source_grounded",
        "all_rollback_controls_source_grounded",
        "all_switch_edges_source_grounded",
        "duplicate_readiness_check_keys_found_false",
        "duplicate_legacy_projection_keys_found_false",
        "duplicate_cleanup_task_keys_found_false",
        "duplicate_rollback_control_keys_found_false",
        "orphan_switch_edges_found_false",
    ]:
        if validation[key] is not True:
            errors.append(f"validation flag failed: {key}")
    validation["valid"] = not errors
    validation["errors"] = errors
    return validation
