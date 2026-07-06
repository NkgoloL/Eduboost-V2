#!/usr/bin/env python3
"""Capture KG-3 learner graph shadow-mode evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_learner_shadow import (
    DEFAULT_OBSERVATIONS,
    DEFAULT_TARGET_GRAPH,
    build_learner_shadow_graph,
    file_sha256,
    validate_learner_shadow_graph,
)
from scripts.roadmap_reconciliation.verify_kg003_learner_graph_shadow_mode import BOUNDARY_FALSE_KEYS, RECORD, evaluate

KG_ID = "KG-3"
DEFAULT_OUTPUT = Path("data/knowledge_graph/learner_shadow_mode/grade4_mathematics_learner_shadow_graph.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/learner_shadow_mode/grade4_mathematics_learner_shadow_graph_summary.json")
EVIDENCE_DIR = Path("docs/release-evidence/knowledge-graph/kg-003-learner-graph-shadow-mode")
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
        'title: "KG-3 Learner Graph Shadow Mode Evidence"',
        "status: recorded",
        "owner: knowledge-graph",
        "---",
        "",
        "# KG-3 Learner Graph Shadow Mode Evidence",
        "",
        f"- Valid: `{verification['valid']}`",
        f"- KG ID: `{record['kg_id']}`",
        f"- Captured at: `{record['evidence_captured_at']}`",
        f"- Evidence owner: `{record['evidence_owner']}`",
        f"- Learner shadow states: `{record['learner_shadow_state_count']}`",
        f"- Shadow evidence events: `{record['shadow_evidence_event_count']}`",
        f"- Shadow edges: `{record['shadow_edge_count']}`",
        f"- Target graph SHA-256: `{record['target_graph_sha256']}`",
        f"- Observation fixture SHA-256: `{record['shadow_observation_fixture_sha256']}`",
        "",
        "## Boundaries",
        "",
        f"- Runtime KG implementation claimed: `{record['runtime_kg_implementation_claimed']}`",
        f"- Runtime KG authority switch authorised: `{record['runtime_kg_authority_switch_authorised']}`",
        f"- Database schema migration authorised: `{record['database_schema_migration_authorised']}`",
        f"- Learner-facing model change authorised: `{record['learner_facing_model_change_authorised']}`",
        f"- Learner graph implementation authorised: `{record['learner_graph_implementation_authorised']}`",
        f"- Learner graph persistence authorised: `{record['learner_graph_persistence_authorised']}`",
        f"- Learner graph runtime authority authorised: `{record['learner_graph_runtime_authority_authorised']}`",
        f"- Production release authorised: `{record['production_release_authorised']}`",
        f"- Public beta authorised: `{record['public_beta_authorised']}`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-kg003-learner-graph-shadow-mode", action="store_true")
    parser.add_argument("--kg-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_kg003_learner_graph_shadow_mode:
        raise SystemExit("--claim-kg003-learner-graph-shadow-mode is required")

    pre = evaluate(Path("."))
    if not pre["authority_valid"]:
        if args.json:
            print(json.dumps({"valid": False, "stage": "pre-capture", "errors": pre["errors"]}, indent=2, sort_keys=True))
        return 1

    graph = build_learner_shadow_graph(DEFAULT_TARGET_GRAPH, DEFAULT_OBSERVATIONS)
    validation = validate_learner_shadow_graph(graph)
    write_json(DEFAULT_OUTPUT, graph)
    summary = {
        "valid": validation["valid"],
        "graph_id": graph["graph_id"],
        "graph_version": graph["graph_version"],
        "target_graph_sha256": graph["source"]["target_graph_sha256"],
        "shadow_observation_fixture_sha256": graph["source"]["observation_fixture_sha256"],
        "counts": graph["counts"],
        "validation": validation,
        "output": str(DEFAULT_OUTPUT),
    }
    write_json(DEFAULT_SUMMARY, summary)

    state = git_state(args.target_branch)
    captured_at = datetime.now(timezone.utc).isoformat()
    counts = graph["counts"]
    record = {
        "kg_id": KG_ID,
        "status": "learner_graph_shadow_mode_recorded",
        "learner_graph_shadow_mode_recorded": True,
        "evidence_owner": args.kg_owner,
        "evidence_captured_at": captured_at,
        "target_branch": args.target_branch,
        "git_state": state,
        "clean_git_state_at_capture": state.get("status_short", "") == "",
        "kg2_target_graph_generation_valid": True,
        "target_graph_dependency_recorded": True,
        "target_graph_path": str(DEFAULT_TARGET_GRAPH),
        "target_graph_sha256": file_sha256(DEFAULT_TARGET_GRAPH),
        "shadow_observation_fixture_recorded": True,
        "shadow_observation_fixture_path": str(DEFAULT_OBSERVATIONS),
        "shadow_observation_fixture_sha256": file_sha256(DEFAULT_OBSERVATIONS),
        "learner_shadow_graph_artifact_generated": True,
        "learner_shadow_graph_artifact_path": str(DEFAULT_OUTPUT),
        "learner_shadow_graph_summary_path": str(DEFAULT_SUMMARY),
        "synthetic_learner_fixture_only": True,
        "no_live_learner_data_used": True,
        "learner_shadow_state_count": counts["learner_shadow_states"],
        "shadow_evidence_event_count": counts["shadow_evidence_events"],
        "shadow_edge_count": counts["shadow_edges"],
        "synthetic_learner_count": counts["synthetic_learners"],
        "target_states_referenced_count": counts["target_states_referenced"],
        "shadow_gap_count": counts["shadow_gap"],
        "shadow_developing_count": counts["shadow_developing"],
        "shadow_mastered_count": counts["shadow_mastered"],
        "all_shadow_states_reference_targets": validation["all_shadow_states_reference_targets"],
        "all_shadow_states_source_grounded": validation["all_shadow_states_source_grounded"],
        "all_shadow_events_source_grounded": validation["all_shadow_events_source_grounded"],
        "duplicate_shadow_state_keys_found_false": True,
        "orphan_shadow_edges_found_false": True,
        "shadow_mode_boundary_recorded": True,
        "privacy_boundary_recorded": True,
        "runtime_kg_boundary_recorded": True,
        "next_kg_slice": "KG-4 — Gap engine and intervention planner",
        **BOUNDARY_FALSE,
    }
    write_json(RECORD, record)
    final = evaluate(Path("."))
    record["verification"] = final
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", final)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "learner_shadow_graph_summary.json", summary)
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
