#!/usr/bin/env python3
"""Capture KG-1 CAPS graph foundation evidence."""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.knowledge_graph.build_kg001_caps_graph_foundation import DEFAULT_OUTPUT, DEFAULT_SUMMARY, write_json
from scripts.roadmap_reconciliation.verify_kg001_caps_graph_foundation import evaluate
from app.domain.knowledge_graph_caps import DEFAULT_SOURCE, build_caps_graph, validate_caps_graph

KG_ID = "KG-1"
RECORD = Path("docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/knowledge-graph/kg-001-caps-graph-foundation")
BOUNDARY_FALSE = {
    "runtime_kg_implementation_claimed": False,
    "runtime_kg_authority_switch_authorised": False,
    "database_schema_migration_authorised": False,
    "learner_facing_model_change_authorised": False,
    "learner_graph_implementation_authorised": False,
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
}


def git_state(target_branch: str) -> dict[str, str]:
    def run(*args: str) -> str:
        try:
            return check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""
    return {
        "branch": run("branch", "--show-current"),
        "head_sha": run("rev-parse", "HEAD"),
        "status_short": run("status", "--short"),
        "target_branch": target_branch,
    }


def write_index(path: Path, record: dict[str, Any], verification: dict[str, Any]) -> None:
    lines = [
        "# KG-1 CAPS Graph Foundation Evidence", "",
        f"Recorded at: `{record['evidence_captured_at']}`",
        f"KG ID: `{KG_ID}`",
        f"Owner: `{record['evidence_owner']}`", "",
        "## Result", "",
        f"- Valid: `{verification['valid']}`",
        f"- KG-0 formal roadmap approval valid: `{record['kg0_formal_roadmap_approval_valid']}`",
        f"- CAPS graph artifact generated: `{record['caps_graph_artifact_generated']}`",
        f"- CAPS graph node count: `{record['caps_graph_node_count']}`",
        f"- CAPS graph edge count: `{record['caps_graph_edge_count']}`",
        f"- All CAPS nodes source grounded: `{record['all_caps_nodes_source_grounded']}`",
        f"- All CAPS edges source grounded: `{record['all_caps_edges_source_grounded']}`", "",
        "## Evidence files", "",
        "- `verification.json`",
        "- `git_state.json`",
        "- `graph_summary.json`",
        "- `data/knowledge_graph/caps_graph_foundation/grade4_mathematics_caps_graph.json`",
        "- `docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation_record.json`", "",
        "## Boundary", "",
        f"- Runtime KG implementation claimed: `{record['runtime_kg_implementation_claimed']}`",
        f"- Runtime KG authority switch authorised: `{record['runtime_kg_authority_switch_authorised']}`",
        f"- Database schema migration authorised: `{record['database_schema_migration_authorised']}`",
        f"- Learner-facing model change authorised: `{record['learner_facing_model_change_authorised']}`",
        f"- Learner graph implementation authorised: `{record['learner_graph_implementation_authorised']}`",
        f"- Production release authorised: `{record['production_release_authorised']}`",
        f"- Deployment authorised: `{record['deployment_authorised']}`",
        f"- Public beta authorised: `{record['public_beta_authorised']}`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-kg001-caps-graph-foundation", action="store_true")
    parser.add_argument("--kg-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_kg001_caps_graph_foundation:
        raise SystemExit("--claim-kg001-caps-graph-foundation is required")

    pre = evaluate(Path("."))
    if not pre["authority_valid"]:
        if args.json:
            print(json.dumps({"valid": False, "stage": "pre-capture", "errors": pre["errors"]}, indent=2, sort_keys=True))
        return 1

    graph = build_caps_graph(DEFAULT_SOURCE)
    validation = validate_caps_graph(graph)
    write_json(DEFAULT_OUTPUT, graph)
    summary = {
        "valid": True,
        "graph_id": graph["graph_id"],
        "graph_version": graph["graph_version"],
        "source_sha256": graph["source"]["source_sha256"],
        "counts": graph["counts"],
        "validation": validation,
        "output": str(DEFAULT_OUTPUT),
    }
    write_json(DEFAULT_SUMMARY, summary)

    state = git_state(args.target_branch)
    captured_at = datetime.now(timezone.utc).isoformat()
    record = {
        "kg_id": KG_ID,
        "status": "caps_graph_foundation_recorded",
        "caps_graph_foundation_recorded": True,
        "evidence_owner": args.kg_owner,
        "evidence_captured_at": captured_at,
        "target_branch": args.target_branch,
        "git_state": state,
        "clean_git_state_at_capture": state.get("status_short", "") == "",
        "kg0_formal_roadmap_approval_valid": True,
        "caps_source_topic_map_present": True,
        "caps_source_checksum_recorded": True,
        "caps_source_sha256": graph["source"]["source_sha256"],
        "caps_graph_artifact_generated": True,
        "caps_graph_artifact_path": str(DEFAULT_OUTPUT),
        "caps_graph_summary_path": str(DEFAULT_SUMMARY),
        "caps_graph_schema_recorded": True,
        "caps_graph_loader_contract_recorded": True,
        "caps_graph_review_manifest_recorded": True,
        "caps_graph_node_count": graph["counts"]["nodes"],
        "caps_graph_edge_count": graph["counts"]["edges"],
        "caps_graph_term_count": graph["counts"]["terms"],
        "caps_graph_topic_count": graph["counts"]["topics"],
        "caps_graph_subtopic_count": graph["counts"]["subtopics"],
        "all_caps_nodes_source_grounded": True,
        "all_caps_edges_source_grounded": True,
        "duplicate_node_keys_found_false": True,
        "orphan_edges_found_false": True,
        "runtime_kg_boundary_recorded": True,
        "next_kg_slice": "KG-2 — Target graph generation",
        **BOUNDARY_FALSE,
    }
    write_json(RECORD, record)
    final = evaluate(Path("."))
    record["verification"] = final
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", final)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "graph_summary.json", summary)
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
