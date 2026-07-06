#!/usr/bin/env python3
"""Capture KG-7 authority-switch readiness and legacy-cleanup evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_authority_switch import (
    BOUNDARY_FALSE_KEYS,
    DEFAULT_PRODUCT_ALIGNMENT_PACK,
    build_authority_switch_readiness_pack,
    file_sha256,
    validate_authority_switch_readiness_pack,
)
from scripts.roadmap_reconciliation.verify_kg007_authority_switch_legacy_cleanup import RECORD, evaluate

KG_ID = "KG-7"
DEFAULT_OUTPUT = Path("data/knowledge_graph/authority_switch/grade4_mathematics_authority_switch_readiness_pack.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/authority_switch/grade4_mathematics_authority_switch_readiness_pack_summary.json")
EVIDENCE_DIR = Path("docs/release-evidence/knowledge-graph/kg-007-authority-switch-legacy-cleanup")
BOUNDARY_FALSE = {key: False for key in BOUNDARY_FALSE_KEYS}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_state(target_branch: str) -> dict[str, str]:
    def run(args: list[str]) -> str:
        try:
            return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""
    return {
        "target_branch": target_branch,
        "branch": run(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "head_sha": run(["git", "rev-parse", "HEAD"]),
        "status_short": run(["git", "status", "--short"]),
    }


def write_index(path: Path, record: dict[str, Any], verification: dict[str, Any]) -> None:
    lines = [
        "---",
        'title: "KG-7 Authority Switch Legacy Cleanup Evidence"',
        "status: recorded",
        "owner: knowledge-graph",
        "---",
        "",
        "# KG-7 Authority Switch and Legacy Cleanup Evidence",
        "",
        f"- Valid: `{verification['valid']}`",
        f"- KG ID: `{record['kg_id']}`",
        f"- Captured at: `{record['evidence_captured_at']}`",
        f"- Evidence owner: `{record['evidence_owner']}`",
        f"- Readiness checks: `{record['authority_readiness_check_count']}`",
        f"- Legacy projection mappings: `{record['legacy_projection_mapping_count']}`",
        f"- Legacy cleanup tasks: `{record['legacy_cleanup_task_count']}`",
        f"- Rollback controls: `{record['rollback_control_count']}`",
        f"- Switch control edges: `{record['switch_control_edge_count']}`",
        f"- KG-6 product alignment SHA-256: `{record['product_alignment_pack_sha256']}`",
        "",
        "## Boundary",
        "",
        f"- Runtime KG authority switch authorised: `{record['runtime_kg_authority_switch_authorised']}`",
        f"- Authority switch executed: `{record['authority_switch_executed']}`",
        f"- Legacy cleanup executed: `{record['legacy_cleanup_executed']}`",
        f"- Database schema migration authorised: `{record['database_schema_migration_authorised']}`",
        f"- Learner-facing model change authorised: `{record['learner_facing_model_change_authorised']}`",
        f"- Production release authorised: `{record['production_release_authorised']}`",
        f"- Deployment authorised: `{record['deployment_authorised']}`",
        f"- Public beta authorised: `{record['public_beta_authorised']}`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-kg007-authority-switch-readiness", action="store_true")
    parser.add_argument("--kg-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_kg007_authority_switch_readiness:
        raise SystemExit("--claim-kg007-authority-switch-readiness is required")

    pre = evaluate(Path("."))
    if not pre["authority_valid"]:
        if args.json:
            print(json.dumps({"valid": False, "stage": "pre-capture", "errors": pre["errors"]}, indent=2, sort_keys=True))
        return 1

    pack = build_authority_switch_readiness_pack(DEFAULT_PRODUCT_ALIGNMENT_PACK)
    validation = validate_authority_switch_readiness_pack(pack)
    write_json(DEFAULT_OUTPUT, pack)
    summary = {
        "valid": validation["valid"],
        "graph_id": pack["graph_id"],
        "graph_version": pack["graph_version"],
        "product_alignment_pack_sha256": pack["source"]["product_alignment_pack_sha256"],
        "counts": pack["counts"],
        "validation": validation,
        "output": str(DEFAULT_OUTPUT),
    }
    write_json(DEFAULT_SUMMARY, summary)

    state = git_state(args.target_branch)
    captured_at = datetime.now(timezone.utc).isoformat()
    counts = pack["counts"]
    record = {
        "kg_id": KG_ID,
        "status": "authority_switch_legacy_cleanup_readiness_recorded",
        "authority_switch_legacy_cleanup_recorded": True,
        "evidence_owner": args.kg_owner,
        "evidence_captured_at": captured_at,
        "target_branch": args.target_branch,
        "git_state": state,
        "clean_git_state_at_capture": state.get("status_short", "") == "",
        "kg6_product_alignment_valid": True,
        "product_alignment_dependency_recorded": True,
        "product_alignment_pack_path": str(DEFAULT_PRODUCT_ALIGNMENT_PACK),
        "product_alignment_pack_sha256": file_sha256(DEFAULT_PRODUCT_ALIGNMENT_PACK),
        "authority_switch_readiness_pack_artifact_generated": True,
        "authority_switch_readiness_pack_artifact_path": str(DEFAULT_OUTPUT),
        "authority_switch_readiness_pack_summary_path": str(DEFAULT_SUMMARY),
        "synthetic_learner_fixture_only": True,
        "no_live_learner_data_used": validation["no_live_learner_data_used"],
        "no_guardian_pii_used": validation["no_guardian_pii_used"],
        "feature_flag_control_count": counts["feature_flag_controls"],
        "authority_readiness_check_count": counts["authority_readiness_checks"],
        "legacy_projection_mapping_count": counts["legacy_projection_mappings"],
        "legacy_cleanup_task_count": counts["legacy_cleanup_tasks"],
        "rollback_control_count": counts["rollback_controls"],
        "switch_control_edge_count": counts["switch_control_edges"],
        "synthetic_learner_count": counts["synthetic_learners"],
        "all_authority_readiness_checks_passed": validation["all_authority_readiness_checks_passed"],
        "all_legacy_projection_mappings_source_grounded": validation["all_legacy_projection_mappings_source_grounded"],
        "all_readiness_checks_source_grounded": validation["all_readiness_checks_source_grounded"],
        "all_cleanup_tasks_source_grounded": validation["all_cleanup_tasks_source_grounded"],
        "all_rollback_controls_source_grounded": validation["all_rollback_controls_source_grounded"],
        "all_switch_edges_source_grounded": validation["all_switch_edges_source_grounded"],
        "all_legacy_projection_mappings_readiness_only": validation["all_legacy_projection_mappings_readiness_only"],
        "all_cleanup_tasks_planned_not_executed": validation["all_cleanup_tasks_planned_not_executed"],
        "all_rollback_controls_available": validation["all_rollback_controls_available"],
        "duplicate_readiness_check_keys_found_false": validation["duplicate_readiness_check_keys_found_false"],
        "duplicate_legacy_projection_keys_found_false": validation["duplicate_legacy_projection_keys_found_false"],
        "duplicate_cleanup_task_keys_found_false": validation["duplicate_cleanup_task_keys_found_false"],
        "duplicate_rollback_control_keys_found_false": validation["duplicate_rollback_control_keys_found_false"],
        "orphan_switch_edges_found_false": validation["orphan_switch_edges_found_false"],
        "feature_flag_boundary_recorded": True,
        "legacy_cleanup_boundary_recorded": True,
        "rollback_boundary_recorded": True,
        "runtime_kg_boundary_recorded": True,
        "next_kg_slice": "KG-8 — Post-switch optimisation and scale review is blocked until an explicit runtime authority activation is approved",
        **BOUNDARY_FALSE,
    }
    write_json(RECORD, record)
    final = evaluate(Path("."))
    record["verification"] = final
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", final)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "authority_switch_readiness_pack_summary.json", summary)
    write_index(EVIDENCE_DIR / "evidence_index.md", record, final)

    if args.require_valid and not final["valid"]:
        if args.json:
            print(json.dumps(final, indent=2, sort_keys=True))
        return 1
    if args.json:
        print(json.dumps(final, indent=2, sort_keys=True))
    else:
        print(f"valid={str(final['valid']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
