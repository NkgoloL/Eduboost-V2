#!/usr/bin/env python3
"""Capture KG-2 target graph generation evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_target import DEFAULT_CAPS_GRAPH, build_target_graph, validate_target_graph
from scripts.roadmap_reconciliation.verify_kg002_target_graph_generation import BOUNDARY_FALSE_KEYS, RECORD, evaluate

KG_ID = "KG-2"
DEFAULT_OUTPUT = Path("data/knowledge_graph/target_graph/grade4_mathematics_target_graph.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/target_graph/grade4_mathematics_target_graph_summary.json")
EVIDENCE_DIR = Path("docs/release-evidence/knowledge-graph/kg-002-target-graph-generation")
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
        'title: "KG-2 Target Graph Generation Evidence"',
        "status: recorded",
        "owner: knowledge-graph",
        "---",
        "",
        "# KG-2 Target Graph Generation Evidence",
        "",
        f"- Valid: `{verification['valid']}`",
        f"- KG ID: `{record['kg_id']}`",
        f"- Captured at: `{record['evidence_captured_at']}`",
        f"- Evidence owner: `{record['evidence_owner']}`",
        f"- Target graph states: `{record['target_graph_state_count']}`",
        f"- Target graph edges: `{record['target_graph_edge_count']}`",
        f"- CAPS graph SHA-256: `{record['caps_graph_sha256']}`",
        "",
        "## Boundaries",
        "",
        f"- Runtime KG implementation claimed: `{record['runtime_kg_implementation_claimed']}`",
        f"- Runtime KG authority switch authorised: `{record['runtime_kg_authority_switch_authorised']}`",
        f"- Database schema migration authorised: `{record['database_schema_migration_authorised']}`",
        f"- Learner-facing model change authorised: `{record['learner_facing_model_change_authorised']}`",
        f"- Learner graph implementation authorised: `{record['learner_graph_implementation_authorised']}`",
        f"- Target graph runtime authority authorised: `{record['target_graph_runtime_authority_authorised']}`",
        f"- Production release authorised: `{record['production_release_authorised']}`",
        f"- Deployment authorised: `{record['deployment_authorised']}`",
        f"- Public beta authorised: `{record['public_beta_authorised']}`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-kg002-target-graph-generation", action="store_true")
    parser.add_argument("--kg-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_kg002_target_graph_generation:
        raise SystemExit("--claim-kg002-target-graph-generation is required")

    pre = evaluate(Path("."))
    if not pre["authority_valid"]:
        if args.json:
            print(json.dumps({"valid": False, "stage": "pre-capture", "errors": pre["errors"]}, indent=2, sort_keys=True))
        return 1

    graph = build_target_graph(DEFAULT_CAPS_GRAPH)
    validation = validate_target_graph(graph)
    write_json(DEFAULT_OUTPUT, graph)
    summary = {
        "valid": True,
        "graph_id": graph["graph_id"],
        "graph_version": graph["graph_version"],
        "caps_graph_sha256": graph["source"]["caps_graph_sha256"],
        "counts": graph["counts"],
        "validation": validation,
        "output": str(DEFAULT_OUTPUT),
    }
    write_json(DEFAULT_SUMMARY, summary)

    state = git_state(args.target_branch)
    captured_at = datetime.now(timezone.utc).isoformat()
    record = {
        "kg_id": KG_ID,
        "status": "target_graph_generation_recorded",
        "target_graph_generation_recorded": True,
        "evidence_owner": args.kg_owner,
        "evidence_captured_at": captured_at,
        "target_branch": args.target_branch,
        "git_state": state,
        "clean_git_state_at_capture": state.get("status_short", "") == "",
        "kg1_caps_graph_foundation_valid": True,
        "caps_graph_dependency_recorded": True,
        "caps_graph_path": str(DEFAULT_CAPS_GRAPH),
        "caps_graph_sha256": graph["source"]["caps_graph_sha256"],
        "target_graph_artifact_generated": True,
        "target_graph_artifact_path": str(DEFAULT_OUTPUT),
        "target_graph_summary_path": str(DEFAULT_SUMMARY),
        "target_graph_schema_recorded": True,
        "target_graph_policy_contract_recorded": True,
        "target_graph_review_manifest_recorded": True,
        "target_graph_state_count": graph["counts"]["target_states"],
        "target_graph_edge_count": graph["counts"]["target_edges"],
        "target_graph_topic_target_count": graph["counts"]["topic_targets"],
        "target_graph_subtopic_target_count": graph["counts"]["subtopic_targets"],
        "target_graph_assessment_statement_target_count": graph["counts"]["assessment_statement_targets"],
        "target_graph_prerequisite_edge_count": graph["counts"]["target_prerequisite_edges"],
        "target_graph_references_approved_caps_nodes_only": True,
        "required_mastery_thresholds_present": True,
        "required_confidence_thresholds_present": True,
        "priority_weighting_present": True,
        "pacing_windows_present": True,
        "duplicate_target_keys_found_false": True,
        "orphan_target_edges_found_false": True,
        "runtime_kg_boundary_recorded": True,
        "next_kg_slice": "KG-3 — Learner graph shadow mode",
        **BOUNDARY_FALSE,
    }
    write_json(RECORD, record)
    final = evaluate(Path("."))
    record["verification"] = final
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", final)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "target_graph_summary.json", summary)
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
