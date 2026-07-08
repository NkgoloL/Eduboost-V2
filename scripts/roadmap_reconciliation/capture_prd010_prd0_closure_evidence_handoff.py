#!/usr/bin/env python3
"""Capture PRD-0.10 PRD-0 closure evidence and PRD-1 handoff."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from scripts.production_readiness.apply_prd010_prd0_closure_evidence_handoff import apply as apply_handoff_authority
from scripts.production_readiness.audit_prd010_prd0_closure_evidence_handoff import (
    FALSE_KEYS,
    PRD_ID,
    RECORD,
    REGISTER,
    SNAPSHOT,
    TRUE_KEYS,
    closure_snapshot,
)
from scripts.roadmap_reconciliation.verify_prd010_prd0_closure_evidence_handoff import evaluate

EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-010-prd0-closure-evidence-handoff")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_state(target_branch: str) -> dict:
    def run(args: list[str]) -> str | None:
        try:
            return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    status = run(["git", "status", "--short"])
    return {
        "branch": run(["git", "branch", "--show-current"]),
        "head_sha": run(["git", "rev-parse", "HEAD"]),
        "status_short": status,
        "target_branch": target_branch,
        "git_available": status is not None,
    }


def update_register(now: str) -> dict:
    register = read_json(REGISTER)
    register["last_recorded_item"] = PRD_ID
    register["last_recorded_at"] = now
    register["next_authorised_item"] = "PRD-1"
    register["status"] = "prd_0_closed_prd_1_handoff_recorded"
    register["prd0_closed"] = True
    register["prd0_closed_at"] = now
    register["prd1_handoff_authorised"] = True
    register["prd1_blocked_until_prd0_closure"] = False
    register.setdefault("current_truth", {})["prd1_blocked_until_prd0_closure"] = False
    register["current_truth"]["prd0_closed"] = True
    register["current_truth"]["prd1_handoff_authorised"] = True
    # Keep the historical gate key for older PRD-0 verifiers, but add terminal truth.
    register.setdefault("gates", {})["prd1_blocked_until_prd0_closure"] = True
    register["gates"]["prd1_handoff_authorised_after_prd0_closure"] = True
    for item in register.get("prd0_sequence", []):
        if item.get("prd_id") == PRD_ID:
            item["authorised"] = True
            item["status"] = "recorded"
    for item in register.get("production_readiness_sequence", []):
        if item.get("prd_id") == "PRD-1":
            item["authorised"] = True
            item["status"] = "authorised"
        elif item.get("prd_id") != "PRD-1":
            item.setdefault("authorised", False)
            item.setdefault("status", "blocked")
    # PRD-0.10 authorises the PRD-1 workstream handoff, but it does not execute PRD-1 implementation.
    register.setdefault("authority_boundaries", {})["prd1_implementation_authorised"] = False
    write_json(REGISTER, register)
    return register


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd010-prd0-closure-evidence-handoff", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd010_prd0_closure_evidence_handoff:
        raise SystemExit("must pass --claim-prd010-prd0-closure-evidence-handoff")

    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    now = datetime.now(timezone.utc).isoformat()
    state = git_state(args.target_branch)
    apply_handoff_authority(Path("."), write_files=True)
    register = update_register(now)
    snapshot = closure_snapshot(Path("."), captured_at=now)
    write_json(SNAPSHOT, snapshot)

    record = read_json(RECORD)
    record.update({
        "prd_id": PRD_ID,
        "stream_id": "PRD-PRODUCTION-READINESS",
        "status": "prd0_closed_prd1_handoff_recorded",
        "prd009_repository_hygiene_generated_local_artifact_audit_valid": before.get("prd009_repository_hygiene_generated_local_artifact_audit_valid") is True,
        "all_prd0_predecessors_valid": snapshot.get("all_prd0_predecessors_valid") is True,
        "prd0_closure_evidence_recorded": True,
        "prd0_handoff_to_prd1_recorded": True,
        "prd0_sequence_complete": snapshot.get("register_summary", {}).get("prd0_sequence_complete") is True,
        "prd0_closure_checklist_refreshed": True,
        "prd1_handoff_document_refreshed": True,
        "prd1_handoff_authorised": True,
        "next_authorised_item": "PRD-1",
        "no_prd1_implementation_performed": True,
        "prd1_implementation_authorised": False,
        "evidence_owner": args.prd_owner,
        "evidence_captured_at": now,
        "target_branch": args.target_branch,
        "clean_git_state_at_capture": state["status_short"] == "" if state.get("git_available") else None,
        "git_state": state,
    })
    for key in TRUE_KEYS:
        record[key] = True
    for key in FALSE_KEYS:
        record[key] = False
    write_json(RECORD, record)

    after = evaluate(Path("."))
    record["verification"] = after
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", after)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "production_readiness_register_terminal_snapshot.json", register)
    write_json(EVIDENCE_DIR / "prd0_closure_evidence_handoff_snapshot.json", snapshot)
    (EVIDENCE_DIR / "evidence_index.md").write_text(
        "# PRD-0.10 PRD-0 Closure Evidence and PRD-1 Handoff Evidence\n\n"
        f"- Captured at: {now}\n"
        f"- Evidence owner: {args.prd_owner}\n"
        f"- Target branch: {args.target_branch}\n"
        f"- Valid: {after.get('valid')}\n"
        f"- Authority valid: {after.get('authority_valid')}\n"
        f"- All PRD-0 predecessors valid: {after.get('all_prd0_predecessors_valid')}\n"
        f"- PRD-0 closure evidence recorded: {after.get('prd0_closure_evidence_recorded')}\n"
        f"- PRD-1 handoff recorded: {after.get('prd0_handoff_to_prd1_recorded')}\n"
        f"- Next authorised item: {after.get('register_next_authorised_item')}\n"
        "- PRD-1 implementation performed by PRD-0.10: false\n"
        "- Production release/deployment/beta/billing/live learner traffic/new KG scope: false\n",
        encoding="utf-8",
    )

    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.10 evidence valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
