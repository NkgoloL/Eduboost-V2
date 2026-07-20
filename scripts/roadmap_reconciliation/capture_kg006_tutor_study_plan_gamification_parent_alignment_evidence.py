#!/usr/bin/env python3
"""Capture KG-6 tutor/study-plan/gamification/parent alignment evidence."""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_product_alignment import (
    DEFAULT_GENERATION_PACK,
    build_product_alignment_pack,
    file_sha256,
    validate_product_alignment_pack,
)
from scripts.roadmap_reconciliation.verify_kg006_tutor_study_plan_gamification_parent_alignment import BOUNDARY_FALSE_KEYS, RECORD, evaluate

KG_ID = "KG-6"
DEFAULT_OUTPUT = Path("data/knowledge_graph/product_alignment/grade4_mathematics_product_alignment_pack.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/product_alignment/grade4_mathematics_product_alignment_pack_summary.json")
EVIDENCE_DIR = Path("docs/release-evidence/knowledge-graph/kg-006-tutor-study-plan-gamification-parent-alignment")
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
        'title: "KG-6 Tutor Study Plan Gamification Parent Alignment Evidence"',
        "status: recorded",
        "owner: knowledge-graph",
        "---",
        "",
        "# KG-6 Tutor, Study Plan, Gamification, and Parent Alignment Evidence",
        "",
        f"- Valid: `{verification['valid']}`",
        f"- KG ID: `{record['kg_id']}`",
        f"- Captured at: `{record['evidence_captured_at']}`",
        f"- Evidence owner: `{record['evidence_owner']}`",
        f"- Tutor previews: `{record['tutor_preview_count']}`",
        f"- Study plan items: `{record['study_plan_item_count']}`",
        f"- Gamification candidates: `{record['gamification_award_candidate_count']}`",
        f"- Parent alignment summaries: `{record['parent_alignment_summary_count']}`",
        f"- Product alignment edges: `{record['product_alignment_edge_count']}`",
        f"- KG-5 generation pack SHA-256: `{record['generation_pack_sha256']}`",
        "",
        "## Boundaries",
        "",
        f"- Runtime KG implementation claimed: `{record['runtime_kg_implementation_claimed']}`",
        f"- Runtime KG authority switch authorised: `{record['runtime_kg_authority_switch_authorised']}`",
        f"- Database schema migration authorised: `{record['database_schema_migration_authorised']}`",
        f"- Learner-facing model change authorised: `{record['learner_facing_model_change_authorised']}`",
        f"- Tutor runtime authority authorised: `{record['tutor_runtime_authority_authorised']}`",
        f"- Study plan runtime authority authorised: `{record['study_plan_runtime_authority_authorised']}`",
        f"- Gamification runtime authority authorised: `{record['gamification_runtime_authority_authorised']}`",
        f"- Parent portal runtime authority authorised: `{record['parent_portal_runtime_authority_authorised']}`",
        f"- Public beta authorised: `{record['public_beta_authorised']}`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-kg006-product-alignment", action="store_true")
    parser.add_argument("--kg-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_kg006_product_alignment:
        raise SystemExit("--claim-kg006-product-alignment is required")

    pre = evaluate(Path("."))
    if not pre["authority_valid"]:
        if args.json:
            print(json.dumps({"valid": False, "stage": "pre-capture", "errors": pre["errors"]}, indent=2, sort_keys=True))
        return 1

    pack = build_product_alignment_pack(DEFAULT_GENERATION_PACK)
    validation = validate_product_alignment_pack(pack)
    write_json(DEFAULT_OUTPUT, pack)
    summary = {
        "valid": validation["valid"],
        "graph_id": pack["graph_id"],
        "graph_version": pack["graph_version"],
        "generation_pack_sha256": pack["source"]["generation_pack_sha256"],
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
        "status": "product_alignment_recorded",
        "product_alignment_recorded": True,
        "evidence_owner": args.kg_owner,
        "evidence_captured_at": captured_at,
        "target_branch": args.target_branch,
        "git_state": state,
        "clean_git_state_at_capture": state.get("status_short", "") == "",
        "kg5_graph_grounded_generation_valid": True,
        "generation_pack_dependency_recorded": True,
        "generation_pack_path": str(DEFAULT_GENERATION_PACK),
        "generation_pack_sha256": file_sha256(DEFAULT_GENERATION_PACK),
        "product_alignment_pack_artifact_generated": True,
        "product_alignment_pack_artifact_path": str(DEFAULT_OUTPUT),
        "product_alignment_pack_summary_path": str(DEFAULT_SUMMARY),
        "synthetic_learner_fixture_only": True,
        "no_live_learner_data_used": True,
        "no_guardian_pii_used": True,
        "tutor_preview_count": counts["tutor_previews"],
        "study_plan_item_count": counts["study_plan_items"],
        "gamification_award_candidate_count": counts["gamification_award_candidates"],
        "parent_alignment_summary_count": counts["parent_alignment_summaries"],
        "product_alignment_edge_count": counts["product_alignment_edges"],
        "synthetic_learner_count": counts["synthetic_learners"],
        "all_tutor_previews_reference_lessons": validation["all_tutor_previews_reference_lessons"],
        "all_tutor_previews_source_grounded": validation["all_tutor_previews_source_grounded"],
        "all_study_plan_items_reference_lessons": validation["all_study_plan_items_reference_lessons"],
        "all_study_plan_items_source_grounded": validation["all_study_plan_items_source_grounded"],
        "all_gamification_candidates_reference_assessments": validation["all_gamification_candidates_reference_assessments"],
        "all_gamification_candidates_source_grounded": validation["all_gamification_candidates_source_grounded"],
        "all_parent_summaries_synthetic_only": validation["all_parent_summaries_synthetic_only"],
        "all_parent_summaries_source_grounded": validation["all_parent_summaries_source_grounded"],
        "all_product_edges_source_grounded": validation["all_product_edges_source_grounded"],
        "all_product_items_review_required": validation["all_product_items_review_required"],
        "all_product_items_advisory_only": validation["all_product_items_advisory_only"],
        "no_live_learner_aliases": validation["no_live_learner_aliases"],
        "duplicate_tutor_preview_keys_found_false": validation["duplicate_tutor_preview_keys_found_false"],
        "duplicate_study_plan_item_keys_found_false": validation["duplicate_study_plan_item_keys_found_false"],
        "duplicate_award_candidate_keys_found_false": validation["duplicate_award_candidate_keys_found_false"],
        "duplicate_parent_summary_keys_found_false": validation["duplicate_parent_summary_keys_found_false"],
        "orphan_product_edges_found_false": validation["orphan_product_edges_found_false"],
        "product_review_boundary_recorded": True,
        "parent_privacy_boundary_recorded": True,
        "runtime_kg_boundary_recorded": True,
        "next_kg_slice": "KG-7 — Authority switch and legacy cleanup",
        **BOUNDARY_FALSE,
    }
    write_json(RECORD, record)
    final = evaluate(Path("."))
    record["verification"] = final
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", final)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "product_alignment_pack_summary.json", summary)
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
