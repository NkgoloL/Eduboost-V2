#!/usr/bin/env python3
"""Capture KG-5 graph-grounded lesson and assessment generation evidence."""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_grounded_generation import (
    DEFAULT_GAP_PLAN,
    DEFAULT_TARGET_GRAPH,
    build_graph_grounded_generation_pack,
    file_sha256,
    validate_graph_grounded_generation_pack,
)
from scripts.roadmap_reconciliation.verify_kg005_graph_grounded_lesson_assessment_generation import BOUNDARY_FALSE_KEYS, RECORD, evaluate

KG_ID = "KG-5"
DEFAULT_OUTPUT = Path("data/knowledge_graph/grounded_generation/grade4_mathematics_graph_grounded_generation_pack.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/grounded_generation/grade4_mathematics_graph_grounded_generation_pack_summary.json")
EVIDENCE_DIR = Path("docs/release-evidence/knowledge-graph/kg-005-graph-grounded-lesson-assessment-generation")
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
        'title: "KG-5 Graph-Grounded Lesson and Assessment Generation Evidence"',
        "status: recorded",
        "owner: knowledge-graph",
        "---",
        "",
        "# KG-5 Graph-Grounded Lesson and Assessment Generation Evidence",
        "",
        f"- Valid: `{verification['valid']}`",
        f"- KG ID: `{record['kg_id']}`",
        f"- Captured at: `{record['evidence_captured_at']}`",
        f"- Evidence owner: `{record['evidence_owner']}`",
        f"- Lesson drafts: `{record['lesson_draft_count']}`",
        f"- Assessment drafts: `{record['assessment_draft_count']}`",
        f"- Generation edges: `{record['generation_edge_count']}`",
        f"- Gap plan SHA-256: `{record['gap_plan_sha256']}`",
        f"- Target graph SHA-256: `{record['target_graph_sha256']}`",
        "",
        "## Boundaries",
        "",
        f"- Runtime KG implementation claimed: `{record['runtime_kg_implementation_claimed']}`",
        f"- Runtime KG authority switch authorised: `{record['runtime_kg_authority_switch_authorised']}`",
        f"- Database schema migration authorised: `{record['database_schema_migration_authorised']}`",
        f"- Learner-facing model change authorised: `{record['learner_facing_model_change_authorised']}`",
        f"- Generation runtime authority authorised: `{record['generation_runtime_authority_authorised']}`",
        f"- Assessment runtime authority authorised: `{record['assessment_runtime_authority_authorised']}`",
        f"- LLM provider call authorised: `{record['llm_provider_call_authorised']}`",
        f"- Production release authorised: `{record['production_release_authorised']}`",
        f"- Public beta authorised: `{record['public_beta_authorised']}`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-kg005-graph-grounded-generation", action="store_true")
    parser.add_argument("--kg-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_kg005_graph_grounded_generation:
        raise SystemExit("--claim-kg005-graph-grounded-generation is required")

    pre = evaluate(Path("."))
    if not pre["authority_valid"]:
        if args.json:
            print(json.dumps({"valid": False, "stage": "pre-capture", "errors": pre["errors"]}, indent=2, sort_keys=True))
        return 1

    pack = build_graph_grounded_generation_pack(DEFAULT_GAP_PLAN, DEFAULT_TARGET_GRAPH)
    validation = validate_graph_grounded_generation_pack(pack)
    write_json(DEFAULT_OUTPUT, pack)
    summary = {
        "valid": validation["valid"],
        "graph_id": pack["graph_id"],
        "graph_version": pack["graph_version"],
        "gap_plan_sha256": pack["source"]["gap_plan_sha256"],
        "target_graph_sha256": pack["source"]["target_graph_sha256"],
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
        "status": "graph_grounded_generation_recorded",
        "graph_grounded_generation_recorded": True,
        "evidence_owner": args.kg_owner,
        "evidence_captured_at": captured_at,
        "target_branch": args.target_branch,
        "git_state": state,
        "clean_git_state_at_capture": state.get("status_short", "") == "",
        "kg4_gap_engine_intervention_planner_valid": True,
        "gap_plan_dependency_recorded": True,
        "gap_plan_path": str(DEFAULT_GAP_PLAN),
        "gap_plan_sha256": file_sha256(DEFAULT_GAP_PLAN),
        "target_graph_dependency_recorded": True,
        "target_graph_path": str(DEFAULT_TARGET_GRAPH),
        "target_graph_sha256": file_sha256(DEFAULT_TARGET_GRAPH),
        "generation_pack_artifact_generated": True,
        "generation_pack_artifact_path": str(DEFAULT_OUTPUT),
        "generation_pack_summary_path": str(DEFAULT_SUMMARY),
        "synthetic_learner_fixture_only": True,
        "no_live_learner_data_used": True,
        "lesson_draft_count": counts["lesson_drafts"],
        "assessment_draft_count": counts["assessment_drafts"],
        "generation_edge_count": counts["generation_edges"],
        "target_states_referenced_count": counts["target_states_referenced"],
        "human_review_required_item_count": counts["human_review_required_items"],
        "all_lessons_reference_interventions": validation["all_lessons_reference_interventions"],
        "all_lessons_source_grounded": validation["all_lessons_source_grounded"],
        "all_assessments_reference_lessons": validation["all_assessments_reference_lessons"],
        "all_assessments_source_grounded": validation["all_assessments_source_grounded"],
        "all_generation_items_review_required": validation["all_generation_items_review_required"],
        "all_lessons_advisory_only": validation["all_lessons_advisory_only"],
        "all_assessments_advisory_only": validation["all_assessments_advisory_only"],
        "no_live_learner_aliases": validation["no_live_learner_aliases"],
        "duplicate_lesson_keys_found_false": validation["duplicate_lesson_keys_found_false"],
        "duplicate_assessment_keys_found_false": validation["duplicate_assessment_keys_found_false"],
        "orphan_generation_edges_found_false": validation["orphan_generation_edges_found_false"],
        "human_review_boundary_recorded": True,
        "privacy_boundary_recorded": True,
        "runtime_kg_boundary_recorded": True,
        "next_kg_slice": "KG-6 — Tutor, study plan, gamification, and parent alignment",
        **BOUNDARY_FALSE,
    }
    write_json(RECORD, record)
    final = evaluate(Path("."))
    record["verification"] = final
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", final)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "graph_grounded_generation_pack_summary.json", summary)
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
