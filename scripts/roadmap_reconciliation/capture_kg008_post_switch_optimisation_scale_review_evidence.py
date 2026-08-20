#!/usr/bin/env python3
"""Capture KG-8 post-switch optimisation and scale review evidence."""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_post_switch_review import (
    DEFAULT_RUNTIME_ACTIVATION_PACK,
    build_post_switch_review_pack,
    file_sha256,
    validate_post_switch_review_pack,
)
from scripts.roadmap_reconciliation.verify_kg008_post_switch_optimisation_scale_review import RECORD, evaluate

KG_ID = "KG-8"
DEFAULT_OUTPUT = Path("data/knowledge_graph/post_switch_review/grade4_mathematics_post_switch_optimisation_scale_review_pack.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/post_switch_review/grade4_mathematics_post_switch_optimisation_scale_review_pack_summary.json")
EVIDENCE_DIR = Path("docs/release-evidence/knowledge-graph/kg-008-post-switch-optimisation-scale-review")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_state(target_branch: str) -> dict[str, str]:
    def run(args: list[str]) -> str:
        try:
            return check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
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
        'title: "KG-8 Post-Switch Optimisation and Scale Review Evidence"',
        "status: recorded",
        "owner: knowledge-graph",
        "---",
        "",
        "# KG-8 Post-Switch Optimisation and Scale Review Evidence",
        "",
        f"- Valid: `{verification['valid']}`",
        f"- KG ID: `{record['kg_id']}`",
        f"- Captured at: `{record['evidence_captured_at']}`",
        f"- Evidence owner: `{record['evidence_owner']}`",
        f"- Optimisation candidates: `{record['optimisation_candidate_count']}`",
        f"- Scale review checks: `{record['scale_review_check_count']}`",
        f"- Monitoring requirements: `{record['monitoring_requirement_count']}`",
        f"- Rollback observability checks: `{record['rollback_observability_check_count']}`",
        f"- Post-switch review edges: `{record['post_switch_review_edge_count']}`",
        "",
        "## Runtime KG state reviewed",
        "",
        f"- Runtime KG implementation claimed: `{record['runtime_kg_implementation_claimed']}`",
        f"- Runtime KG authority switch authorised: `{record['runtime_kg_authority_switch_authorised']}`",
        f"- Authority switch executed: `{record['authority_switch_executed']}`",
        "",
        "## Boundaries still controlled elsewhere",
        "",
        f"- Production release authorised: `{record['production_release_authorised']}`",
        f"- Deployment authorised: `{record['deployment_authorised']}`",
        f"- Public beta authorised: `{record['public_beta_authorised']}`",
        f"- Billing launch authorised: `{record['billing_launch_authorised']}`",
        f"- Live payment processing authorised: `{record['live_payment_processing_authorised']}`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-kg008-post-switch-review", action="store_true")
    parser.add_argument("--kg-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_kg008_post_switch_review:
        raise SystemExit("--claim-kg008-post-switch-review is required")

    pre = evaluate(Path("."))
    if not pre["authority_valid"]:
        if args.json:
            print(json.dumps({"valid": False, "stage": "pre-capture", "errors": pre["errors"]}, indent=2, sort_keys=True))
        return 1

    pack = build_post_switch_review_pack(DEFAULT_RUNTIME_ACTIVATION_PACK)
    validation = validate_post_switch_review_pack(pack)
    write_json(DEFAULT_OUTPUT, pack)
    summary = {
        "valid": validation["valid"],
        "graph_id": pack["graph_id"],
        "graph_version": pack["graph_version"],
        "runtime_activation_pack_sha256": pack["source"]["runtime_activation_pack_sha256"],
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
        "status": "post_switch_optimisation_scale_review_recorded",
        "post_switch_optimisation_scale_review_recorded": True,
        "evidence_owner": args.kg_owner,
        "evidence_captured_at": captured_at,
        "target_branch": args.target_branch,
        "git_state": state,
        "clean_git_state_at_capture": state.get("status_short", "") == "",
        "kgact001_controlled_runtime_activation_valid": True,
        "runtime_activation_pack_path": str(DEFAULT_RUNTIME_ACTIVATION_PACK),
        "runtime_activation_pack_sha256": file_sha256(DEFAULT_RUNTIME_ACTIVATION_PACK),
        "post_switch_review_pack_artifact_generated": True,
        "post_switch_review_pack_artifact_path": str(DEFAULT_OUTPUT),
        "post_switch_review_pack_summary_path": str(DEFAULT_SUMMARY),
        "post_switch_go_no_go_review_approved": True,
        "optimisation_backlog_reviewed": True,
        "scale_review_completed": True,
        "monitoring_observability_review_completed": True,
        "rollback_observability_review_completed": True,
        "popia_post_switch_boundary_reviewed": True,
        "post_switch_boundary_recorded": True,
        "optimisation_candidate_count": counts["optimisation_candidates"],
        "scale_review_check_count": counts["scale_review_checks"],
        "monitoring_requirement_count": counts["monitoring_requirements"],
        "rollback_observability_check_count": counts["rollback_observability_checks"],
        "post_switch_review_edge_count": counts["post_switch_review_edges"],
        "activation_control_count_inherited": counts["activation_controls_inherited"],
        "readiness_check_count_inherited": counts["readiness_checks_inherited"],
        "legacy_projection_mapping_count_inherited": counts["legacy_projection_mappings_inherited"],
        "rollback_control_count_inherited": counts["rollback_controls_inherited"],
        "all_optimisation_candidates_source_grounded": validation["all_optimisation_candidates_source_grounded"],
        "all_scale_review_checks_source_grounded": validation["all_scale_review_checks_source_grounded"],
        "all_monitoring_requirements_source_grounded": validation["all_monitoring_requirements_source_grounded"],
        "all_rollback_observability_checks_source_grounded": validation["all_rollback_observability_checks_source_grounded"],
        "all_post_switch_edges_source_grounded": validation["all_post_switch_edges_source_grounded"],
        "all_post_switch_items_review_only": validation["all_post_switch_items_review_only"],
        "duplicate_post_switch_item_keys_found_false": validation["duplicate_post_switch_item_keys_found_false"],
        "orphan_post_switch_edges_found_false": validation["orphan_post_switch_edges_found_false"],
        "runtime_kg_implementation_claimed": True,
        "runtime_kg_authority_switch_authorised": True,
        "authority_switch_executed": True,
        "kg_roadmap_completed_through_kg8": True,
        "database_schema_migration_authorised": False,
        "learner_facing_model_change_authorised": False,
        "learner_graph_persistence_authorised": False,
        "legacy_cleanup_executed": False,
        "llm_provider_call_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "optimisation_execution_authorised": False,
        "scale_load_test_execution_authorised": False,
        "next_recommended_step": "KG roadmap closure report or new approved production/public-beta roadmap; do not infer deployment from KG-8",
    }
    write_json(RECORD, record)
    final = evaluate(Path("."))
    record["verification"] = final
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", final)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "post_switch_review_pack_summary.json", summary)
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
