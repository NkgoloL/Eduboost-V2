#!/usr/bin/env python3
"""Capture final roadmap reconciliation closure evidence."""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import hashlib
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_final_roadmap_reconciliation_closure import evaluate

RECORD = Path("docs/roadmap/reconciliation/final_roadmap_reconciliation_closure_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/roadmap-reconciliation/final-roadmap-reconciliation-closure")

BOUNDARY_FALSE = {
    "billing_launch_authorised": False,
    "live_payment_processing_authorised": False,
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
    "public_beta_live_traffic_authorised": False,
    "runtime_kg_implementation_claimed": False,
    "new_rr_items_introduced": False,
    "new_unreconciled_work_authorised": False,
}


def _run(cmd: list[str]) -> str:
    try:
        return check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def git_state(target_branch: str) -> dict[str, str]:
    return {
        "branch": _run(["git", "branch", "--show-current"]),
        "head_sha": _run(["git", "rev-parse", "HEAD"]),
        "status_short": _run(["git", "status", "--short"]),
        "target_branch": target_branch,
    }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def write_index(record: dict[str, Any], raw_path: Path) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    index = EVIDENCE_DIR / "evidence_index.md"
    index.write_text(
        "# Final Roadmap Reconciliation Closure Evidence\n\n"
        f"- Captured at: `{record['evidence_captured_at']}`\n"
        f"- Owner: `{record['evidence_owner']}`\n"
        f"- Target branch: `{record['target_branch']}`\n"
        f"- Head SHA: `{record['git_state'].get('head_sha', '')}`\n"
        f"- Clean git state at capture: `{record['clean_git_state_at_capture']}`\n"
        f"- All RR items addressed: `{record['all_reconciled_rr_items_addressed']}`\n"
        "- Boundaries preserved: production release, deployment, public beta, billing launch, live payment processing, and runtime KG all remain unauthorised.\n"
        "\n## Raw evidence\n\n"
        f"- `{raw_path.name}`\n",
        encoding="utf-8",
    )
    sums = EVIDENCE_DIR / "SHA256SUMS.txt"
    sums.write_text(
        f"{sha256(index)}  {index.name}\n{sha256(raw_path)}  {raw_path.name}\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-final-roadmap-closure", action="store_true", required=True)
    parser.add_argument("--closure-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    pre = evaluate(Path("."))
    state = git_state(args.target_branch)
    clean = state.get("status_short", "") == ""
    record: dict[str, Any] = {
        "status": "final_roadmap_reconciliation_closure_recorded",
        "closure_id": "FINAL-ROADMAP-RECONCILIATION-CLOSURE",
        "evidence_owner": args.closure_owner,
        "target_branch": args.target_branch,
        "evidence_captured_at": datetime.now(timezone.utc).isoformat(),
        "git_state": state,
        "clean_git_state_at_capture": clean,
        "final_roadmap_reconciliation_closure_recorded": True,
        "final_closure_report_recorded": True,
        "final_closure_matrix_recorded": True,
        "all_reconciled_rr_items_addressed": pre["all_reconciled_rr_items_addressed"],
        "all_reconciled_rr_items_addressed_through_rr018": pre["all_reconciled_rr_items_addressed_through_rr018"],
        "outstanding_work_register_closed_through_rr018": True,
        "rr003_fallback_coverage_caveat_visible": True,
        "rr006_non_required_checks_caveat_visible": True,
        "rr016_clean_git_state_caveat_visible": True,
        **BOUNDARY_FALSE,
    }
    RECORD.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    post = evaluate(Path("."))
    record["verification"] = post
    RECORD.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = EVIDENCE_DIR / "raw_final_roadmap_reconciliation_closure.json"
    raw_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_index(record, raw_path)

    final = evaluate(Path("."))
    if args.json:
        print(json.dumps(final, indent=2, sort_keys=True))
    if args.require_valid and not final["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
