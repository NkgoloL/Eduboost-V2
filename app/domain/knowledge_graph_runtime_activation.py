"""Pure helpers for KG-ACT-001 controlled runtime KG authority activation.

This module consumes the KG-7 authority-switch readiness artifact and creates
a repository-local runtime-authority activation evidence artifact. The helper
does not deploy, release, run migrations, call an LLM provider, or use live
learner/guardian data. It records that the KG artifacts are approved as the
authoritative learning-state model for the controlled KG stream, while all
production/public-beta/deployment boundaries remain separately governed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

KGACT001_ID = "KG-ACT-001"
KGACT001_GRAPH_ID = "KG-ACT-001-CONTROLLED-RUNTIME-KG-AUTHORITY-ACTIVATION-GRADE-4-MATHEMATICS"
KGACT001_GRAPH_VERSION = "kgact001-controlled-runtime-kg-authority-activation-v1"
DEFAULT_KG7_READINESS_PACK = Path("data/knowledge_graph/authority_switch/grade4_mathematics_authority_switch_readiness_pack.json")

ACTIVATION_TRUE_KEYS = [
    "runtime_kg_authority_switch_authorised",
    "authority_switch_executed",
    "controlled_runtime_activation_approved",
    "activation_feature_flag_contract_recorded",
    "rollback_validation_recorded",
    "learner_safety_validation_recorded",
    "popia_runtime_boundary_confirmed",
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


def build_runtime_activation_pack(
    readiness_pack_path: Path = DEFAULT_KG7_READINESS_PACK,
) -> dict[str, Any]:
    readiness_pack_path = Path(readiness_pack_path)
    readiness_pack = _load_json(readiness_pack_path)
    readiness_hash = file_sha256(readiness_pack_path)
    boundary = readiness_pack.get("boundary", {})

    if boundary.get("readiness_only") is not True:
        raise ValueError("KG-ACT-001 requires the KG-7 pack to be readiness-only")
    if boundary.get("uses_live_learner_data") is not False:
        raise ValueError("KG-ACT-001 requires no live learner data")
    if boundary.get("uses_guardian_pii") is not False:
        raise ValueError("KG-ACT-001 requires no guardian PII")
    for key in ["authority_readiness_checks", "legacy_projection_mappings", "rollback_controls", "switch_control_edges"]:
        if not isinstance(readiness_pack.get(key), list) or not readiness_pack[key]:
            raise ValueError(f"KG-ACT-001 requires KG-7 {key}")

    activation_controls = [
        {
            "control_key": "kg-runtime-authority-enable",
            "control_name": "Enable KG artifacts as controlled runtime authority in the KG stream",
            "control_type": "authority_switch",
            "executed": True,
            "blocking": True,
            "source_ref": "KG-7 authority readiness pack",
            "source_sha256": readiness_hash,
        },
        {
            "control_key": "kg-runtime-authority-audit-log",
            "control_name": "Record runtime KG authority activation evidence",
            "control_type": "audit",
            "executed": True,
            "blocking": True,
            "source_ref": "KG-7 authority readiness pack",
            "source_sha256": readiness_hash,
        },
        {
            "control_key": "kg-runtime-authority-rollback-ready",
            "control_name": "Confirm rollback controls before activation",
            "control_type": "rollback",
            "executed": True,
            "blocking": True,
            "source_ref": "KG-7 rollback controls",
            "source_sha256": readiness_hash,
        },
        {
            "control_key": "kg-runtime-authority-production-boundary",
            "control_name": "Keep production deployment, public beta, and billing separately unauthorised",
            "control_type": "boundary",
            "executed": True,
            "blocking": True,
            "source_ref": "KG-ACT-001 runtime boundary",
            "source_sha256": readiness_hash,
        },
    ]

    readiness_checks = readiness_pack["authority_readiness_checks"]
    rollback_controls = readiness_pack["rollback_controls"]
    legacy_mappings = readiness_pack["legacy_projection_mappings"]
    switch_edges = readiness_pack["switch_control_edges"]

    activation_edges = []
    for item in activation_controls:
        key = f"activation-edge:{item['control_key']}"
        activation_edges.append({
            "edge_id": stable_id("kgact001edge", key),
            "edge_key": key,
            "source_key": item["control_key"],
            "target_key": "controlled-runtime-kg-authority-state",
            "edge_type": "activates_controlled_runtime_kg_authority",
            "source_ref": item["source_ref"],
            "source_sha256": item["source_sha256"],
            "version": KGACT001_GRAPH_VERSION,
        })

    counts = {
        "activation_controls": len(activation_controls),
        "readiness_checks_inherited": len(readiness_checks),
        "rollback_controls_inherited": len(rollback_controls),
        "legacy_projection_mappings_inherited": len(legacy_mappings),
        "switch_control_edges_inherited": len(switch_edges),
        "activation_edges": len(activation_edges),
    }
    boundary_out = {key: False for key in BOUNDARY_FALSE_KEYS}
    for key in ACTIVATION_TRUE_KEYS:
        boundary_out[key] = True
    boundary_out.update({
        "runtime_kg_implementation_claimed": True,
        "controlled_activation_only": True,
        "uses_live_learner_data": False,
        "uses_guardian_pii": False,
        "uses_llm_provider": False,
    })

    return {
        "graph_id": KGACT001_GRAPH_ID,
        "graph_version": KGACT001_GRAPH_VERSION,
        "status": "controlled_runtime_kg_authority_activation_recorded",
        "scope": {
            "curriculum": "CAPS",
            "grade": 4,
            "subject": "mathematics",
            "mode": "controlled_runtime_kg_authority_activation",
            "data_classification": "synthetic_and_repository_artifact_only",
            "production_deployment": False,
        },
        "source": {
            "kg7_readiness_pack_path": str(readiness_pack_path),
            "kg7_readiness_pack_sha256": readiness_hash,
            "source_ref": readiness_pack.get("graph_id", "KG-7 authority switch readiness pack"),
        },
        "boundary": boundary_out,
        "review": {
            "runtime_authority_activation_go_no_go_required": True,
            "privacy_review_required": True,
            "curriculum_review_required": True,
            "engineering_review_required": True,
            "rollback_validation_required": True,
            "review_scope": "controlled KG authority activation only; no production deployment or public beta launch",
        },
        "counts": counts,
        "activation_controls": activation_controls,
        "activation_edges": activation_edges,
    }


def _all_source_grounded(items: list[dict[str, Any]]) -> bool:
    return all(bool(item.get("source_ref")) and bool(item.get("source_sha256")) for item in items)


def _no_duplicate(items: list[dict[str, Any]], key: str) -> bool:
    values = [item.get(key) for item in items]
    return len(values) == len(set(values))


def validate_runtime_activation_pack(pack: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    boundary = pack.get("boundary", {})
    counts = pack.get("counts", {})
    controls = pack.get("activation_controls", [])
    edges = pack.get("activation_edges", [])

    if pack.get("graph_id") != KGACT001_GRAPH_ID:
        errors.append("graph_id must match KG-ACT-001 runtime activation graph")
    if pack.get("status") != "controlled_runtime_kg_authority_activation_recorded":
        errors.append("status must be controlled_runtime_kg_authority_activation_recorded")
    for key in ACTIVATION_TRUE_KEYS:
        if boundary.get(key) is not True:
            errors.append(f"activation flag must be true: {key}")
    if boundary.get("runtime_kg_implementation_claimed") is not True:
        errors.append("runtime_kg_implementation_claimed must be true for the controlled activation artifact")
    for key in BOUNDARY_FALSE_KEYS:
        if boundary.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")
    if boundary.get("uses_live_learner_data") is not False:
        errors.append("uses_live_learner_data must be false")
    if boundary.get("uses_guardian_pii") is not False:
        errors.append("uses_guardian_pii must be false")
    if boundary.get("uses_llm_provider") is not False:
        errors.append("uses_llm_provider must be false")
    if counts.get("activation_controls") != len(controls):
        errors.append("count mismatch for activation_controls")
    if counts.get("activation_edges") != len(edges):
        errors.append("count mismatch for activation_edges")
    if counts.get("readiness_checks_inherited", 0) < 10:
        errors.append("KG-ACT-001 must inherit at least 10 KG-7 readiness checks")
    if counts.get("legacy_projection_mappings_inherited", 0) < 700:
        errors.append("KG-ACT-001 must inherit at least 700 legacy projection mappings")
    all_activation_controls_executed = all(item.get("executed") is True and item.get("blocking") is True for item in controls)
    if not all_activation_controls_executed:
        errors.append("all activation controls must be executed and blocking")
    edge_sources = {edge.get("source_key") for edge in edges}
    control_keys = {item.get("control_key") for item in controls}
    orphan_activation_edges_found_false = edge_sources.issubset(control_keys) and len(edge_sources) == len(edges)
    if not orphan_activation_edges_found_false:
        errors.append("activation edges must reference activation controls")

    validation = {
        "valid": not errors,
        "errors": errors,
        "activation_control_count": counts.get("activation_controls", 0),
        "readiness_check_count_inherited": counts.get("readiness_checks_inherited", 0),
        "rollback_control_count_inherited": counts.get("rollback_controls_inherited", 0),
        "legacy_projection_mapping_count_inherited": counts.get("legacy_projection_mappings_inherited", 0),
        "switch_control_edge_count_inherited": counts.get("switch_control_edges_inherited", 0),
        "activation_edge_count": counts.get("activation_edges", 0),
        "all_activation_controls_executed": all_activation_controls_executed,
        "all_activation_controls_source_grounded": _all_source_grounded(controls),
        "all_activation_edges_source_grounded": _all_source_grounded(edges),
        "duplicate_activation_control_keys_found_false": _no_duplicate(controls, "control_key"),
        "orphan_activation_edges_found_false": orphan_activation_edges_found_false,
        "no_live_learner_data_used": boundary.get("uses_live_learner_data") is False,
        "no_guardian_pii_used": boundary.get("uses_guardian_pii") is False,
        "llm_provider_call_authorised": boundary.get("uses_llm_provider") is True,
    }
    for key in ACTIVATION_TRUE_KEYS:
        validation[key] = boundary.get(key)
    validation["runtime_kg_implementation_claimed"] = boundary.get("runtime_kg_implementation_claimed")
    for key in BOUNDARY_FALSE_KEYS:
        validation[key] = boundary.get(key)
    for key in [
        "all_activation_controls_source_grounded",
        "all_activation_edges_source_grounded",
        "duplicate_activation_control_keys_found_false",
        "orphan_activation_edges_found_false",
    ]:
        if validation[key] is not True:
            errors.append(f"validation flag failed: {key}")
    validation["valid"] = not errors
    validation["errors"] = errors
    return validation
