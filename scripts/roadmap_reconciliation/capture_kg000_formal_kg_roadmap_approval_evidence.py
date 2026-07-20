#!/usr/bin/env python3
"""Capture KG-0 formal KG roadmap approval evidence."""
from __future__ import annotations
import argparse, json, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from scripts.roadmap_reconciliation.verify_kg000_formal_kg_roadmap_approval import evaluate
RECORD = Path("docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/knowledge-graph/kg-000-formal-kg-roadmap-approval")
BOUNDARY_FALSE = {"runtime_kg_implementation_claimed": False, "runtime_kg_authority_switch_authorised": False, "database_schema_migration_authorised": False, "learner_facing_model_change_authorised": False, "production_release_authorised": False, "deployment_authorised": False, "release_tag_authorised": False, "public_beta_authorised": False, "billing_launch_authorised": False, "live_payment_processing_authorised": False}

def git_value(args: list[str]) -> str:
    try: return check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception: return ""

def git_state(target_branch: str) -> dict[str, str]:
    return {"branch": git_value(["rev-parse", "--abbrev-ref", "HEAD"]), "head_sha": git_value(["rev-parse", "HEAD"]), "status_short": git_value(["status", "--short"]), "target_branch": target_branch}

def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-kg000-formal-kg-roadmap-approval", action="store_true")
    parser.add_argument("--kg-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_kg000_formal_kg_roadmap_approval:
        raise SystemExit("--claim-kg000-formal-kg-roadmap-approval is required")
    pre = evaluate(Path("."))
    if not pre["authority_valid"]:
        if args.json: print(json.dumps({"valid": False, "errors": pre["errors"], "stage": "pre-capture"}, indent=2, sort_keys=True))
        raise SystemExit(1)
    state = git_state(args.target_branch)
    captured_at = datetime.now(timezone.utc).isoformat()
    record = {"kg_id": "KG-0", "status": "formal_kg_roadmap_approval_recorded", "formal_kg_roadmap_approval_recorded": True, "evidence_owner": args.kg_owner, "evidence_captured_at": captured_at, "target_branch": args.target_branch, "git_state": state, "clean_git_state_at_capture": state.get("status_short", "") == "", "final_roadmap_reconciliation_closure_valid": True, "adr_030_recorded": True, "kg_roadmap_register_recorded": True, "kg_implementation_roadmap_recorded": True, "kg_formalization_package_manifest_recorded": True, "kg_0_to_kg_8_sequence_recorded": True, "runtime_kg_boundary_recorded": True, "kg_next_work_rule_recorded": True, "next_kg_slice": "KG-1 — CAPS graph foundation", **BOUNDARY_FALSE}
    write_json(RECORD, record)
    final = evaluate(Path("."))
    record["verification"] = final
    write_json(RECORD, record)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", final)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    (EVIDENCE_DIR / "evidence_index.md").write_text("# KG-0 Formal KG Roadmap Approval Evidence\n\n" f"Captured at: `{captured_at}`\n\n" f"Owner: `{args.kg_owner}`\n\n" "## Evidence files\n\n- `verification.json`\n- `git_state.json`\n- `docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval_record.json`\n\n" "## Boundary\n\nRuntime KG implementation claimed: false  \nRuntime KG authority switch authorised: false  \nDatabase schema migration authorised: false  \nLearner-facing model change authorised: false  \nProduction release authorised: false  \nDeployment authorised: false  \nPublic beta authorised: false  \nBilling launch authorised: false\n", encoding="utf-8")
    if args.require_valid and not final["valid"]:
        if args.json: print(json.dumps(final, indent=2, sort_keys=True))
        raise SystemExit(1)
    if args.json: print(json.dumps(final, indent=2, sort_keys=True))
    else: print("valid=" + str(final["valid"]).lower())
if __name__ == "__main__": main()
