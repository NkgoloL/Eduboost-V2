"""Pure helpers for KG-8 post-switch optimisation and scale review.

KG-8 consumes the controlled runtime KG authority activation artifact from
KG-ACT-001 and creates a repository-local post-switch review evidence artifact.
The helper does not deploy, run database migrations, release to public beta,
process live learner traffic, call an LLM provider, or launch billing. It records
that the controlled runtime KG authority state has been reviewed for scale,
observability, optimisation, and rollback readiness inside the approved KG
stream.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

KG8_ID = "KG-8"
KG8_GRAPH_ID = "KG-8-POST-SWITCH-OPTIMISATION-SCALE-REVIEW-GRADE-4-MATHEMATICS"
KG8_GRAPH_VERSION = "kg008-post-switch-optimisation-scale-review-v1"
DEFAULT_RUNTIME_ACTIVATION_PACK = Path("data/knowledge_graph/runtime_activation/grade4_mathematics_runtime_kg_activation_pack.json")

REQUIRED_RUNTIME_TRUE_KEYS = [
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "authority_switch_executed",
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


def _item(key: str, name: str, kind: str, source_ref: str, source_sha256: str, priority: str = "P1") -> dict[str, Any]:
    return {
        "key": key,
        "id": stable_id("kg008", key),
        "name": name,
        "kind": kind,
        "priority": priority,
        "status": "reviewed",
        "post_switch_review_only": True,
        "source_ref": source_ref,
        "source_sha256": source_sha256,
        "version": KG8_GRAPH_VERSION,
    }


def build_post_switch_review_pack(
    runtime_activation_pack_path: Path = DEFAULT_RUNTIME_ACTIVATION_PACK,
) -> dict[str, Any]:
    runtime_activation_pack_path = Path(runtime_activation_pack_path)
    activation_pack = _load_json(runtime_activation_pack_path)
    activation_hash = file_sha256(runtime_activation_pack_path)
    boundary = activation_pack.get("boundary", {})
    counts = activation_pack.get("counts", {})

    for key in REQUIRED_RUNTIME_TRUE_KEYS:
        if boundary.get(key) is not True:
            raise ValueError(f"KG-8 requires KG-ACT-001 runtime activation flag true: {key}")
    for key in BOUNDARY_FALSE_KEYS:
        if boundary.get(key) is not False:
            raise ValueError(f"KG-8 requires protected boundary false: {key}")
    if boundary.get("uses_live_learner_data") is not False:
        raise ValueError("KG-8 requires no live learner data in review evidence")
    if boundary.get("uses_guardian_pii") is not False:
        raise ValueError("KG-8 requires no guardian PII in review evidence")

    source_ref = activation_pack.get("graph_id", "KG-ACT-001 runtime activation pack")
    optimisation_candidates = [
        _item("kg8-opt-cache-target-lookups", "Cache target graph lookups for repeated lesson paths", "optimisation_candidate", source_ref, activation_hash, "P1"),
        _item("kg8-opt-batch-gap-validation", "Batch advisory gap validation for synthetic learner cohorts", "optimisation_candidate", source_ref, activation_hash, "P1"),
        _item("kg8-opt-evidence-artifact-compaction", "Compact generated evidence artifacts without losing source hashes", "optimisation_candidate", source_ref, activation_hash, "P2"),
        _item("kg8-opt-review-queue-prioritisation", "Prioritise human review queue by prerequisite depth and CAPS coverage", "optimisation_candidate", source_ref, activation_hash, "P1"),
        _item("kg8-opt-parent-summary-projection", "Keep parent summaries source-grounded and PII-free", "optimisation_candidate", source_ref, activation_hash, "P1"),
        _item("kg8-opt-rollback-drift-signal", "Add rollback drift signal for controlled KG authority state", "optimisation_candidate", source_ref, activation_hash, "P1"),
        _item("kg8-opt-generation-pack-index", "Index graph-grounded lesson and assessment draft references", "optimisation_candidate", source_ref, activation_hash, "P2"),
        _item("kg8-opt-scale-fixture-expansion-plan", "Define fixture expansion plan before any live learner cohort", "optimisation_candidate", source_ref, activation_hash, "P1"),
    ]
    scale_review_checks = [
        _item("kg8-scale-activation-controls", "Activation controls remain complete and source-grounded", "scale_review_check", source_ref, activation_hash, "P0"),
        _item("kg8-scale-readiness-inheritance", "Inherited KG-7 readiness checks remain visible", "scale_review_check", source_ref, activation_hash, "P0"),
        _item("kg8-scale-legacy-projection-volume", "Legacy projection mapping volume is recorded", "scale_review_check", source_ref, activation_hash, "P1"),
        _item("kg8-scale-rollback-coverage", "Rollback controls remain available after activation", "scale_review_check", source_ref, activation_hash, "P0"),
        _item("kg8-scale-no-live-learner-data", "Review evidence excludes live learner data", "scale_review_check", source_ref, activation_hash, "P0"),
        _item("kg8-scale-no-guardian-pii", "Review evidence excludes guardian PII", "scale_review_check", source_ref, activation_hash, "P0"),
        _item("kg8-scale-no-llm-provider-call", "Scale review does not call an LLM provider", "scale_review_check", source_ref, activation_hash, "P0"),
        _item("kg8-scale-no-db-migration", "Database schema migration remains unauthorised", "scale_review_check", source_ref, activation_hash, "P0"),
        _item("kg8-scale-release-boundary", "Production and public-beta boundaries remain closed", "scale_review_check", source_ref, activation_hash, "P0"),
        _item("kg8-scale-repeatable-build", "Post-switch review artifact is deterministic and repeatable", "scale_review_check", source_ref, activation_hash, "P1"),
    ]
    monitoring_requirements = [
        _item("kg8-monitor-runtime-authority-state", "Monitor controlled runtime KG authority state", "monitoring_requirement", source_ref, activation_hash, "P0"),
        _item("kg8-monitor-rollback-readiness", "Monitor rollback readiness and drift", "monitoring_requirement", source_ref, activation_hash, "P0"),
        _item("kg8-monitor-review-queue-depth", "Monitor human review queue depth", "monitoring_requirement", source_ref, activation_hash, "P1"),
        _item("kg8-monitor-source-grounding-errors", "Monitor source-grounding validation failures", "monitoring_requirement", source_ref, activation_hash, "P0"),
        _item("kg8-monitor-popia-boundary", "Monitor POPIA boundary violations", "monitoring_requirement", source_ref, activation_hash, "P0"),
        _item("kg8-monitor-graph-artifact-size", "Monitor graph artifact size and growth", "monitoring_requirement", source_ref, activation_hash, "P2"),
        _item("kg8-monitor-generation-draft-volume", "Monitor generated lesson and assessment draft volume", "monitoring_requirement", source_ref, activation_hash, "P2"),
        _item("kg8-monitor-parent-summary-privacy", "Monitor parent summary privacy boundary", "monitoring_requirement", source_ref, activation_hash, "P0"),
    ]
    rollback_observability_checks = [
        _item("kg8-rollback-feature-flag", "Rollback feature flag remains documented", "rollback_observability_check", source_ref, activation_hash, "P0"),
        _item("kg8-rollback-projection", "Legacy projection rollback path remains available", "rollback_observability_check", source_ref, activation_hash, "P0"),
        _item("kg8-rollback-evidence", "Rollback evidence capture path remains available", "rollback_observability_check", source_ref, activation_hash, "P0"),
        _item("kg8-rollback-boundary", "Rollback does not require deployment/public-beta/billing authority", "rollback_observability_check", source_ref, activation_hash, "P0"),
        _item("kg8-rollback-safety", "Rollback path preserves learner safety boundary", "rollback_observability_check", source_ref, activation_hash, "P0"),
        _item("kg8-rollback-popia", "Rollback path preserves POPIA boundary", "rollback_observability_check", source_ref, activation_hash, "P0"),
    ]
    all_items = optimisation_candidates + scale_review_checks + monitoring_requirements + rollback_observability_checks
    post_switch_edges = []
    for item in all_items:
        edge_key = f"post-switch-review-edge:{item['key']}"
        post_switch_edges.append({
            "edge_id": stable_id("kg008edge", edge_key),
            "edge_key": edge_key,
            "source_key": item["key"],
            "target_key": "kg8-post-switch-optimisation-scale-review",
            "edge_type": "supports_post_switch_review",
            "source_ref": item["source_ref"],
            "source_sha256": item["source_sha256"],
            "version": KG8_GRAPH_VERSION,
        })

    boundary_out = {key: False for key in BOUNDARY_FALSE_KEYS}
    boundary_out.update({
        "runtime_kg_implementation_claimed": True,
        "runtime_kg_authority_switch_authorised": True,
        "authority_switch_executed": True,
        "post_switch_review_only": True,
        "optimisation_execution_authorised": False,
        "scale_load_test_execution_authorised": False,
        "legacy_cleanup_executed": False,
        "uses_live_learner_data": False,
        "uses_guardian_pii": False,
        "uses_llm_provider": False,
    })
    out_counts = {
        "optimisation_candidates": len(optimisation_candidates),
        "scale_review_checks": len(scale_review_checks),
        "monitoring_requirements": len(monitoring_requirements),
        "rollback_observability_checks": len(rollback_observability_checks),
        "post_switch_review_edges": len(post_switch_edges),
        "activation_controls_inherited": int(counts.get("activation_controls", 0)),
        "readiness_checks_inherited": int(counts.get("readiness_checks_inherited", 0)),
        "rollback_controls_inherited": int(counts.get("rollback_controls_inherited", 0)),
        "legacy_projection_mappings_inherited": int(counts.get("legacy_projection_mappings_inherited", 0)),
    }
    return {
        "graph_id": KG8_GRAPH_ID,
        "graph_version": KG8_GRAPH_VERSION,
        "status": "post_switch_optimisation_scale_review_recorded",
        "scope": {
            "curriculum": "CAPS",
            "grade": 4,
            "subject": "mathematics",
            "mode": "post_switch_optimisation_scale_review",
            "data_classification": "synthetic_and_repository_artifact_only",
            "production_deployment": False,
        },
        "source": {
            "runtime_activation_pack_path": str(runtime_activation_pack_path),
            "runtime_activation_pack_sha256": activation_hash,
            "source_ref": source_ref,
        },
        "boundary": boundary_out,
        "review": {
            "post_switch_optimisation_review_required": True,
            "scale_review_required": True,
            "monitoring_review_required": True,
            "rollback_observability_review_required": True,
            "popia_boundary_review_required": True,
            "review_scope": "controlled runtime KG authority stream only; no production deployment, public beta, billing, live learner traffic, or database migration",
        },
        "counts": out_counts,
        "optimisation_candidates": optimisation_candidates,
        "scale_review_checks": scale_review_checks,
        "monitoring_requirements": monitoring_requirements,
        "rollback_observability_checks": rollback_observability_checks,
        "post_switch_review_edges": post_switch_edges,
    }


def _all_source_grounded(items: list[dict[str, Any]]) -> bool:
    return all(bool(item.get("source_ref")) and bool(item.get("source_sha256")) for item in items)


def _all_review_only(items: list[dict[str, Any]]) -> bool:
    return all(item.get("post_switch_review_only") is True for item in items)


def _no_duplicate(items: list[dict[str, Any]], key: str) -> bool:
    values = [item.get(key) for item in items]
    return len(values) == len(set(values))


def validate_post_switch_review_pack(pack: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    boundary = pack.get("boundary", {})
    counts = pack.get("counts", {})
    optimisation = pack.get("optimisation_candidates", [])
    scale = pack.get("scale_review_checks", [])
    monitoring = pack.get("monitoring_requirements", [])
    rollback = pack.get("rollback_observability_checks", [])
    edges = pack.get("post_switch_review_edges", [])
    all_items = optimisation + scale + monitoring + rollback

    if pack.get("graph_id") != KG8_GRAPH_ID:
        errors.append("graph_id must match KG-8 post-switch review graph")
    if pack.get("status") != "post_switch_optimisation_scale_review_recorded":
        errors.append("status must be post_switch_optimisation_scale_review_recorded")
    for key in REQUIRED_RUNTIME_TRUE_KEYS:
        if boundary.get(key) is not True:
            errors.append(f"runtime activation flag must remain true: {key}")
    for key in BOUNDARY_FALSE_KEYS:
        if boundary.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")
    for key in ["optimisation_execution_authorised", "scale_load_test_execution_authorised"]:
        if boundary.get(key) is not False:
            errors.append(f"execution boundary flag must remain false: {key}")
    if boundary.get("uses_live_learner_data") is not False:
        errors.append("uses_live_learner_data must be false")
    if boundary.get("uses_guardian_pii") is not False:
        errors.append("uses_guardian_pii must be false")
    if boundary.get("uses_llm_provider") is not False:
        errors.append("uses_llm_provider must be false")

    expected_counts = {
        "optimisation_candidates": len(optimisation),
        "scale_review_checks": len(scale),
        "monitoring_requirements": len(monitoring),
        "rollback_observability_checks": len(rollback),
        "post_switch_review_edges": len(edges),
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            errors.append(f"count mismatch for {key}")
    if counts.get("optimisation_candidates", 0) < 8:
        errors.append("KG-8 must record at least 8 optimisation candidates")
    if counts.get("scale_review_checks", 0) < 10:
        errors.append("KG-8 must record at least 10 scale review checks")
    if counts.get("monitoring_requirements", 0) < 8:
        errors.append("KG-8 must record at least 8 monitoring requirements")
    if counts.get("rollback_observability_checks", 0) < 6:
        errors.append("KG-8 must record at least 6 rollback observability checks")
    if counts.get("readiness_checks_inherited", 0) < 10:
        errors.append("KG-8 must inherit KG-7 readiness checks through KG-ACT-001")
    if counts.get("legacy_projection_mappings_inherited", 0) < 700:
        errors.append("KG-8 must inherit legacy projection mapping volume")

    edge_sources = {edge.get("source_key") for edge in edges}
    item_keys = {item.get("key") for item in all_items}
    orphan_post_switch_edges_found_false = edge_sources.issubset(item_keys) and len(edge_sources) == len(edges)
    duplicate_item_keys_found_false = _no_duplicate(all_items, "key")

    validation = {
        "valid": not errors,
        "errors": errors,
        "optimisation_candidate_count": counts.get("optimisation_candidates", 0),
        "scale_review_check_count": counts.get("scale_review_checks", 0),
        "monitoring_requirement_count": counts.get("monitoring_requirements", 0),
        "rollback_observability_check_count": counts.get("rollback_observability_checks", 0),
        "post_switch_review_edge_count": counts.get("post_switch_review_edges", 0),
        "activation_control_count_inherited": counts.get("activation_controls_inherited", 0),
        "readiness_check_count_inherited": counts.get("readiness_checks_inherited", 0),
        "rollback_control_count_inherited": counts.get("rollback_controls_inherited", 0),
        "legacy_projection_mapping_count_inherited": counts.get("legacy_projection_mappings_inherited", 0),
        "all_optimisation_candidates_source_grounded": _all_source_grounded(optimisation),
        "all_scale_review_checks_source_grounded": _all_source_grounded(scale),
        "all_monitoring_requirements_source_grounded": _all_source_grounded(monitoring),
        "all_rollback_observability_checks_source_grounded": _all_source_grounded(rollback),
        "all_post_switch_edges_source_grounded": _all_source_grounded(edges),
        "all_post_switch_items_review_only": _all_review_only(all_items),
        "duplicate_post_switch_item_keys_found_false": duplicate_item_keys_found_false,
        "orphan_post_switch_edges_found_false": orphan_post_switch_edges_found_false,
        "no_live_learner_data_used": boundary.get("uses_live_learner_data") is False,
        "no_guardian_pii_used": boundary.get("uses_guardian_pii") is False,
        "llm_provider_call_authorised": boundary.get("uses_llm_provider") is True,
    }
    for key in REQUIRED_RUNTIME_TRUE_KEYS:
        validation[key] = boundary.get(key)
    for key in BOUNDARY_FALSE_KEYS + ["optimisation_execution_authorised", "scale_load_test_execution_authorised"]:
        validation[key] = boundary.get(key)
    for key in [
        "all_optimisation_candidates_source_grounded",
        "all_scale_review_checks_source_grounded",
        "all_monitoring_requirements_source_grounded",
        "all_rollback_observability_checks_source_grounded",
        "all_post_switch_edges_source_grounded",
        "all_post_switch_items_review_only",
        "duplicate_post_switch_item_keys_found_false",
        "orphan_post_switch_edges_found_false",
    ]:
        if validation[key] is not True:
            errors.append(f"validation flag failed: {key}")
    validation["valid"] = not errors
    validation["errors"] = errors
    return validation
