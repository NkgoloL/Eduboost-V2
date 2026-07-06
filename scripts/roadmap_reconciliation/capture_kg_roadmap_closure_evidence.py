#!/usr/bin/env python3
"""Capture final KG roadmap closure evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.knowledge_graph.audit_kg_roadmap_closure import KG_RECORDS, audit, matrix_status
from scripts.roadmap_reconciliation.verify_kg_roadmap_closure import RECORD, evaluate

CLOSURE_ID = "KG-ROADMAP-CLOSURE"
KG8_RECORD = Path("docs/roadmap/knowledge_graph/kg_008_post_switch_optimisation_scale_review_record.json")
KGACT001_RECORD = Path("docs/roadmap/knowledge_graph/kg_act_001_controlled_runtime_kg_authority_activation_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/knowledge-graph/kg-roadmap-closure")
MATRIX = Path("docs/roadmap/knowledge_graph/kg_roadmap_closure_matrix.json")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


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
        'title: "KG Roadmap Closure Evidence"',
        "status: recorded",
        "owner: knowledge-graph",
        "---",
        "",
        "# KG Roadmap Closure Evidence",
        "",
        f"- Valid: `{verification['valid']}`",
        f"- Closure ID: `{record['closure_id']}`",
        f"- Captured at: `{record['evidence_captured_at']}`",
        f"- Evidence owner: `{record['evidence_owner']}`",
        f"- KG item count: `{record['kg_item_count']}`",
        f"- KG roadmap completed through KG-8: `{record['kg_roadmap_completed_through_kg8']}`",
        "",
        "## Runtime KG state",
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
        "",
        "## Preserved caveat",
        "",
        "- KG-8 non-required GitHub Actions `kg008-check` failed because the runner called `pytest` directly and it was not on `PATH`; the required repository authority gate passed. This closure workflow uses `python3 -m pytest`.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-kg-roadmap-closure", action="store_true")
    parser.add_argument("--kg-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_kg_roadmap_closure:
        raise SystemExit("--claim-kg-roadmap-closure is required")

    pre = evaluate(Path("."))
    if not pre["authority_valid"]:
        if args.json:
            print(json.dumps({"valid": False, "stage": "pre-capture", "errors": pre["errors"]}, indent=2, sort_keys=True))
        return 1

    kg8 = read_json(KG8_RECORD)
    kgact001 = read_json(KGACT001_RECORD)
    rows = matrix_status(Path("."))
    state = git_state(args.target_branch)
    captured_at = datetime.now(timezone.utc).isoformat()
    matrix = read_json(MATRIX)
    matrix["status"] = "kg_roadmap_closed"
    matrix["closed_at"] = captured_at
    matrix["kg_items"] = rows
    write_json(MATRIX, matrix)

    record = {
        "closure_id": CLOSURE_ID,
        "status": "kg_roadmap_closure_recorded",
        "kg_roadmap_closure_recorded": True,
        "evidence_owner": args.kg_owner,
        "evidence_captured_at": captured_at,
        "target_branch": args.target_branch,
        "git_state": state,
        "clean_git_state_at_capture": state.get("status_short", "") == "",
        "kg_item_count": len(KG_RECORDS),
        "all_kg_items_closed_through_kg8": all(row["record_present"] and row["recorded"] for row in rows),
        "kgact001_activation_gate_closed": kgact001.get("controlled_runtime_kg_authority_activation_recorded") is True,
        "kg8_post_switch_review_closed": kg8.get("post_switch_optimisation_scale_review_recorded") is True,
        "kg_roadmap_completed_through_kg8": kg8.get("kg_roadmap_completed_through_kg8") is True,
        "kg008_non_required_check_pytest_path_caveat_visible": True,
        "kg_roadmap_closed_no_new_kg_slice_authorised": True,
        "new_kg_slice_authorised": False,
        "new_production_or_public_beta_roadmap_authorised": False,
        "runtime_kg_implementation_claimed": kg8.get("runtime_kg_implementation_claimed"),
        "runtime_kg_authority_switch_authorised": kg8.get("runtime_kg_authority_switch_authorised"),
        "authority_switch_executed": kg8.get("authority_switch_executed"),
        "activation_control_count_inherited": kg8.get("activation_control_count_inherited"),
        "readiness_check_count_inherited": kg8.get("readiness_check_count_inherited"),
        "legacy_projection_mapping_count_inherited": kg8.get("legacy_projection_mapping_count_inherited"),
        "rollback_control_count_inherited": kg8.get("rollback_control_count_inherited"),
        "optimisation_candidate_count": kg8.get("optimisation_candidate_count"),
        "scale_review_check_count": kg8.get("scale_review_check_count"),
        "monitoring_requirement_count": kg8.get("monitoring_requirement_count"),
        "rollback_observability_check_count": kg8.get("rollback_observability_check_count"),
        "post_switch_review_edge_count": kg8.get("post_switch_review_edge_count"),
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "next_recommended_step": "Create a new approved roadmap for production release, public beta, billing, live learner traffic, or KG optimisation execution; do not continue the KG implementation sequence by inventing KG-9.",
    }
    write_json(RECORD, record)
    final = evaluate(Path("."))
    record["verification"] = final
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", final)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "kg_closure_matrix_snapshot.json", matrix)
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
