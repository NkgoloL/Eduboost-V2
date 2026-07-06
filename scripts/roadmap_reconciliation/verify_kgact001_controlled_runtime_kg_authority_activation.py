#!/usr/bin/env python3
"""Verify KG-ACT-001 controlled runtime KG authority activation evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.knowledge_graph.audit_kgact001_controlled_runtime_kg_authority_activation import audit

KG_ID = "KG-ACT-001"
RECORD = Path("docs/roadmap/knowledge_graph/kg_act_001_controlled_runtime_kg_authority_activation_record.json")
KG7_RECORD = Path("docs/roadmap/knowledge_graph/kg_007_authority_switch_legacy_cleanup_record.json")

REQUIRED_TRUE_KEYS = [
    "controlled_runtime_kg_authority_activation_recorded",
    "kg7_authority_switch_readiness_valid",
    "runtime_activation_pack_artifact_generated",
    "runtime_activation_go_no_go_approved",
    "activation_feature_flag_contract_recorded",
    "rollback_validation_recorded",
    "learner_safety_validation_recorded",
    "popia_runtime_boundary_confirmed",
    "runtime_activation_boundary_recorded",
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "authority_switch_executed",
    "all_activation_controls_executed",
    "all_activation_controls_source_grounded",
    "all_activation_edges_source_grounded",
    "duplicate_activation_control_keys_found_false",
    "orphan_activation_edges_found_false",
    "kg8_post_switch_optimisation_unblocked",
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


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    record = read_json(root / RECORD)
    kg7 = read_json(root / KG7_RECORD)
    audit_result = audit(root)
    errors: list[str] = []
    warnings: list[str] = []

    kg7_valid = (
        kg7.get("kg_id") == "KG-7"
        and kg7.get("authority_switch_legacy_cleanup_recorded") is True
        and kg7.get("authority_switch_executed") is False
        and kg7.get("runtime_kg_authority_switch_authorised") is False
    )
    if not kg7_valid:
        errors.append("KG-7 authority-switch readiness must be valid and non-executed before KG-ACT-001")
    if record.get("kg_id") != KG_ID:
        errors.append("KG-ACT-001 record must have kg_id KG-ACT-001")
    if not audit_result.get("authority_valid"):
        errors.extend([f"authority audit failed: {err}" for err in audit_result.get("errors", [])])

    captured = record.get("controlled_runtime_kg_authority_activation_recorded") is True
    if captured:
        if not audit_result.get("final_valid"):
            errors.extend([f"final KG-ACT-001 evidence failed: {err}" for err in audit_result.get("errors", [])])
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
        if int(record.get("activation_control_count") or 0) < 4:
            errors.append("KG-ACT-001 activation control count must be at least 4")
        if int(record.get("readiness_check_count_inherited") or 0) < 10:
            errors.append("KG-ACT-001 must inherit at least 10 readiness checks")
        if int(record.get("legacy_projection_mapping_count_inherited") or 0) < 700:
            errors.append("KG-ACT-001 must inherit at least 700 legacy projection mappings")
    else:
        warnings.append("KG-ACT-001 record is still pending activation evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    authority_errors = [
        e for e in errors
        if not e.startswith("record flag must be true")
        and not e.startswith("final KG-ACT-001 evidence failed")
        and "count must" not in e
        and "must inherit" not in e
    ]
    authority_valid = not authority_errors and audit_result.get("authority_valid") is True and kg7_valid
    valid = authority_valid and captured and not errors
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "kg_id": KG_ID,
        "record_path": str(RECORD),
        "errors": errors,
        "warnings": warnings,
        "kg7_authority_switch_readiness_valid": kg7_valid,
        "controlled_runtime_kg_authority_activation_recorded": captured,
        "runtime_activation_pack_artifact_generated": record.get("runtime_activation_pack_artifact_generated") is True,
        "runtime_activation_go_no_go_approved": record.get("runtime_activation_go_no_go_approved") is True,
        "activation_feature_flag_contract_recorded": record.get("activation_feature_flag_contract_recorded") is True,
        "rollback_validation_recorded": record.get("rollback_validation_recorded") is True,
        "learner_safety_validation_recorded": record.get("learner_safety_validation_recorded") is True,
        "popia_runtime_boundary_confirmed": record.get("popia_runtime_boundary_confirmed") is True,
        "runtime_activation_boundary_recorded": record.get("runtime_activation_boundary_recorded") is True,
        "activation_control_count": int(record.get("activation_control_count") or 0),
        "readiness_check_count_inherited": int(record.get("readiness_check_count_inherited") or 0),
        "legacy_projection_mapping_count_inherited": int(record.get("legacy_projection_mapping_count_inherited") or 0),
        "rollback_control_count_inherited": int(record.get("rollback_control_count_inherited") or 0),
        "switch_control_edge_count_inherited": int(record.get("switch_control_edge_count_inherited") or 0),
        "activation_edge_count": int(record.get("activation_edge_count") or 0),
        "all_activation_controls_executed": record.get("all_activation_controls_executed") is True,
        "all_activation_controls_source_grounded": record.get("all_activation_controls_source_grounded") is True,
        "all_activation_edges_source_grounded": record.get("all_activation_edges_source_grounded") is True,
        "duplicate_activation_control_keys_found_false": record.get("duplicate_activation_control_keys_found_false") is True,
        "orphan_activation_edges_found_false": record.get("orphan_activation_edges_found_false") is True,
        "kg8_post_switch_optimisation_unblocked": record.get("kg8_post_switch_optimisation_unblocked") is True,
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
        print(f"KG-ACT-001 controlled runtime KG activation valid: {result['valid']}")
        print(f"KG-ACT-001 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
