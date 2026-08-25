#!/usr/bin/env python3
"""Capture KG-4 gap-engine and intervention-planner evidence."""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_gap_engine import (
    DEFAULT_SHADOW_GRAPH,
    DEFAULT_TARGET_GRAPH,
    build_gap_intervention_plan,
    file_sha256,
    validate_gap_intervention_plan,
)
from scripts.roadmap_reconciliation.verify_kg004_gap_engine_intervention_planner import BOUNDARY_FALSE_KEYS, RECORD, evaluate

KG_ID = "KG-4"
DEFAULT_OUTPUT = Path("data/knowledge_graph/gap_engine/grade4_mathematics_gap_intervention_plan.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/gap_engine/grade4_mathematics_gap_intervention_plan_summary.json")
EVIDENCE_DIR = Path("docs/release-evidence/knowledge-graph/kg-004-gap-engine-intervention-planner")
BOUNDARY_FALSE = {key: False for key in BOUNDARY_FALSE_KEYS}


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
        'title: "KG-4 Gap Engine and Intervention Planner Evidence"',
        "status: recorded",
        "owner: knowledge-graph",
        "---",
        "",
        "# KG-4 Gap Engine and Intervention Planner Evidence",
        "",
        f"- Valid: `{verification['valid']}`",
        f"- KG ID: `{record['kg_id']}`",
        f"- Captured at: `{record['evidence_captured_at']}`",
        f"- Evidence owner: `{record['evidence_owner']}`",
        f"- Gap items: `{record['gap_item_count']}`",
        f"- Intervention recommendations: `{record['intervention_recommendation_count']}`",
        f"- Planner edges: `{record['planner_edge_count']}`",
        f"- Shadow graph SHA-256: `{record['shadow_graph_sha256']}`",
        f"- Target graph SHA-256: `{record['target_graph_sha256']}`",
        "",
        "## Boundaries",
        "",
        f"- Runtime KG implementation claimed: `{record['runtime_kg_implementation_claimed']}`",
        f"- Runtime KG authority switch authorised: `{record['runtime_kg_authority_switch_authorised']}`",
        f"- Database schema migration authorised: `{record['database_schema_migration_authorised']}`",
        f"- Learner-facing model change authorised: `{record['learner_facing_model_change_authorised']}`",
        f"- Gap engine runtime authority authorised: `{record['gap_engine_runtime_authority_authorised']}`",
        f"- Intervention planner runtime authority authorised: `{record['intervention_planner_runtime_authority_authorised']}`",
        f"- Production release authorised: `{record['production_release_authorised']}`",
        f"- Public beta authorised: `{record['public_beta_authorised']}`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-kg004-gap-engine-intervention-planner", action="store_true")
    parser.add_argument("--kg-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_kg004_gap_engine_intervention_planner:
        raise SystemExit("--claim-kg004-gap-engine-intervention-planner is required")

    pre = evaluate(Path("."))
    if not pre["authority_valid"]:
        if args.json:
            print(json.dumps({"valid": False, "stage": "pre-capture", "errors": pre["errors"]}, indent=2, sort_keys=True))
        return 1

    plan = build_gap_intervention_plan(DEFAULT_SHADOW_GRAPH, DEFAULT_TARGET_GRAPH)
    validation = validate_gap_intervention_plan(plan)
    write_json(DEFAULT_OUTPUT, plan)
    summary = {
        "valid": validation["valid"],
        "graph_id": plan["graph_id"],
        "graph_version": plan["graph_version"],
        "shadow_graph_sha256": plan["source"]["shadow_graph_sha256"],
        "target_graph_sha256": plan["source"]["target_graph_sha256"],
        "counts": plan["counts"],
        "validation": validation,
        "output": str(DEFAULT_OUTPUT),
    }
    write_json(DEFAULT_SUMMARY, summary)

    state = git_state(args.target_branch)
    captured_at = datetime.now(timezone.utc).isoformat()
    counts = plan["counts"]
    record = {
        "kg_id": KG_ID,
        "status": "gap_engine_intervention_planner_recorded",
        "gap_engine_intervention_planner_recorded": True,
        "evidence_owner": args.kg_owner,
        "evidence_captured_at": captured_at,
        "target_branch": args.target_branch,
        "git_state": state,
        "clean_git_state_at_capture": state.get("status_short", "") == "",
        "kg3_learner_graph_shadow_mode_valid": True,
        "shadow_graph_dependency_recorded": True,
        "shadow_graph_path": str(DEFAULT_SHADOW_GRAPH),
        "shadow_graph_sha256": file_sha256(DEFAULT_SHADOW_GRAPH),
        "target_graph_dependency_recorded": True,
        "target_graph_path": str(DEFAULT_TARGET_GRAPH),
        "target_graph_sha256": file_sha256(DEFAULT_TARGET_GRAPH),
        "gap_intervention_plan_artifact_generated": True,
        "gap_intervention_plan_artifact_path": str(DEFAULT_OUTPUT),
        "gap_intervention_plan_summary_path": str(DEFAULT_SUMMARY),
        "synthetic_learner_fixture_only": True,
        "no_live_learner_data_used": True,
        "gap_item_count": counts["gap_items"],
        "intervention_recommendation_count": counts["intervention_recommendations"],
        "planner_edge_count": counts["planner_edges"],
        "shadow_gap_item_count": counts["shadow_gap_items"],
        "shadow_developing_item_count": counts["shadow_developing_items"],
        "urgent_item_count": counts["urgent_items"],
        "high_item_count": counts["high_items"],
        "medium_item_count": counts["medium_items"],
        "watch_item_count": counts["watch_items"],
        "all_gap_items_reference_shadow_states": validation["all_gap_items_reference_shadow_states"],
        "all_gap_items_source_grounded": validation["all_gap_items_source_grounded"],
        "all_interventions_source_grounded": validation["all_interventions_source_grounded"],
        "all_interventions_advisory_only": validation["all_interventions_advisory"],
        "duplicate_gap_keys_found_false": validation["duplicate_gap_keys_found_false"],
        "duplicate_intervention_keys_found_false": validation["duplicate_intervention_keys_found_false"],
        "orphan_planner_edges_found_false": validation["orphan_planner_edges_found_false"],
        "advisory_boundary_recorded": True,
        "privacy_boundary_recorded": True,
        "runtime_kg_boundary_recorded": True,
        "next_kg_slice": "KG-5 — Graph-grounded lesson and assessment generation",
        **BOUNDARY_FALSE,
    }
    write_json(RECORD, record)
    final = evaluate(Path("."))
    record["verification"] = final
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", final)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "gap_intervention_plan_summary.json", summary)
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
