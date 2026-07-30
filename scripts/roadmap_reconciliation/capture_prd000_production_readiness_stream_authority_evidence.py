#!/usr/bin/env python3
"""Capture PRD-0.0 production-readiness stream authority evidence."""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.production_readiness.audit_prd000_production_readiness_stream_authority import REGISTER, RECORD
from scripts.roadmap_reconciliation.verify_prd000_production_readiness_stream_authority import evaluate

EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-000-production-readiness-stream-authority")
PRD_ID = "PRD-0.0"
STREAM_ID = "PRD-PRODUCTION-READINESS"


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
        'title: "PRD-0.0 Production Readiness Stream Authority Evidence"',
        "status: recorded",
        "owner: production-readiness",
        "---",
        "",
        "# PRD-0.0 Production Readiness Stream Authority Evidence",
        "",
        f"- Valid: `{verification['valid']}`",
        f"- PRD ID: `{record['prd_id']}`",
        f"- Stream ID: `{record['stream_id']}`",
        f"- Captured at: `{record['evidence_captured_at']}`",
        f"- Evidence owner: `{record['evidence_owner']}`",
        f"- PRD-0 sequence registered: `{record['prd0_sequence_registered']}`",
        f"- PRD-1 blocked until PRD-0 closure: `{record['prd1_blocked_until_prd0_closure']}`",
        "",
        "## Inherited closure truth",
        "",
        f"- RR closure valid: `{record['rr_closure_valid']}`",
        f"- KG closure valid: `{record['kg_closure_valid']}`",
        f"- Runtime KG implementation claimed: `{record['runtime_kg_implementation_claimed']}`",
        f"- Runtime KG authority switch authorised: `{record['runtime_kg_authority_switch_authorised']}`",
        f"- Authority switch executed: `{record['authority_switch_executed']}`",
        "",
        "## Boundaries still controlled elsewhere",
        "",
        f"- Production release authorised: `{record['production_release_authorised']}`",
        f"- Deployment authorised: `{record['deployment_authorised']}`",
        f"- Public beta authorised: `{record['public_beta_authorised']}`",
        f"- Live learner traffic authorised: `{record['live_learner_traffic_authorised']}`",
        f"- Billing launch authorised: `{record['billing_launch_authorised']}`",
        f"- Live payment processing authorised: `{record['live_payment_processing_authorised']}`",
        f"- New KG slice authorised: `{record['new_kg_slice_authorised']}`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd000-production-readiness-stream-authority", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd000_production_readiness_stream_authority:
        raise SystemExit("--claim-prd000-production-readiness-stream-authority is required")

    pre = evaluate(Path("."))
    if not pre["authority_valid"]:
        if args.json:
            print(json.dumps({"valid": False, "stage": "pre-capture", "errors": pre["errors"]}, indent=2, sort_keys=True))
        return 1

    captured_at = datetime.now(timezone.utc).isoformat()
    state = git_state(args.target_branch)
    register = read_json(REGISTER)
    register["status"] = "prd_0_0_authority_recorded"
    register["prd0_sequence"][0]["status"] = "recorded"
    register["prd0_sequence"][0]["authorised"] = True
    register["next_authorised_item"] = "PRD-0.1"
    register["last_recorded_item"] = PRD_ID
    register["last_recorded_at"] = captured_at
    write_json(REGISTER, register)

    record = {
        "prd_id": PRD_ID,
        "stream_id": STREAM_ID,
        "status": "production_readiness_stream_authority_recorded",
        "production_readiness_stream_authority_recorded": True,
        "evidence_owner": args.prd_owner,
        "evidence_captured_at": captured_at,
        "target_branch": args.target_branch,
        "git_state": state,
        "clean_git_state_at_capture": state.get("status_short", "") == "",
        "rr_closure_valid": True,
        "kg_closure_valid": True,
        "prd0_sequence_registered": True,
        "production_readiness_sequence_registered": True,
        "prd1_blocked_until_prd0_closure": True,
        "known_caveats_carried_forward": True,
        "next_authorised_item": "PRD-0.1",
        "runtime_kg_implementation_claimed": True,
        "runtime_kg_authority_switch_authorised": True,
        "authority_switch_executed": True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "live_learner_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "new_kg_slice_authorised": False,
        "prd1_implementation_authorised": False,
    }
    write_json(RECORD, record)
    final = evaluate(Path("."))
    record["verification"] = final
    write_json(RECORD, record)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", final)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    write_json(EVIDENCE_DIR / "production_readiness_register_snapshot.json", register)
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
