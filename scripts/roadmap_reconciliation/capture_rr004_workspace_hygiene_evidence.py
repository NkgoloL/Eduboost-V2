#!/usr/bin/env python3
"""Capture RR-004 workspace hygiene evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_rr004_workspace_hygiene import evaluate
from scripts.workspace_hygiene.audit_workspace_hygiene import collect as collect_workspace_hygiene

RR_ID = "RR-004"
RECORD = Path("docs/roadmap/reconciliation/rr_004_workspace_hygiene_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/roadmap-reconciliation/rr-004-workspace-hygiene")


def _run(args: list[str]) -> dict[str, Any]:
    try:
        proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        return {"command": args, "returncode": proc.returncode, "output": proc.stdout}
    except Exception as exc:
        return {"command": args, "returncode": 127, "output": f"{type(exc).__name__}: {exc}"}


def _git_state(target_branch: str) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    return {
        "branch": run("branch", "--show-current"),
        "head_sha": run("rev-parse", "HEAD"),
        "status_short": run("status", "--short"),
        "target_branch": target_branch,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_index(path: Path, record: dict[str, Any], verification: dict[str, Any]) -> None:
    lines = [
        "# RR-004 Workspace Hygiene Evidence",
        "",
        f"Recorded at: `{record['recorded_at']}`",
        f"RR ID: `{RR_ID}`",
        f"Owner: `{record['hygiene_owner']}`",
        "",
        "## Result",
        "",
        f"- Valid: `{verification['valid']}`",
        f"- Safe cleanup target recorded: `{record['safe_cleanup_target_recorded']}`",
        f"- Tracked-file audit inventory recorded: `{record['tracked_file_audit_inventory_recorded']}`",
        f"- Reproducible scanner counts recorded: `{record['reproducible_scanner_counts_recorded']}`",
        f"- Ignored artifact cleanup dry-run only: `{record['ignored_artifact_cleanup_dry_run_only']}`",
        f"- Tracked file count: `{record['scanner_counts'].get('tracked_file_count')}`",
        f"- Ignored artifact candidate count: `{record['scanner_counts'].get('ignored_artifact_candidate_count')}`",
        "",
        "## Boundary",
        "",
        f"- Production release authorised: `{record['production_release_authorised']}`",
        f"- Deployment authorised: `{record['deployment_authorised']}`",
        f"- Release tag authorised: `{record['release_tag_authorised']}`",
        f"- Public beta authorised: `{record['public_beta_authorised']}`",
        f"- Runtime KG implementation claimed: `{record['runtime_kg_implementation_claimed']}`",
        "",
        "## Raw evidence",
        "",
        "- `raw/record.json`",
        "- `raw/verification.json`",
        "- `raw/workspace_hygiene_audit.json`",
        "- `raw/safe_cleanup_dry_run.json`",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-rr004-workspace-hygiene", action="store_true")
    parser.add_argument("--hygiene-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.claim_rr004_workspace_hygiene:
        raise SystemExit("missing --claim-rr004-workspace-hygiene")

    pre = evaluate(Path("."))
    if not pre.get("authority_valid"):
        payload = {"valid": False, "errors": pre.get("errors", []), "stage": "pre-capture"}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        if args.require_valid:
            return 1

    git_state = _git_state(args.target_branch)
    scanner_counts = collect_workspace_hygiene()
    cleanup_dry_run = _run(["python3", "scripts/workspace_hygiene/safe_cleanup_ignored_artifacts.py", "--dry-run", "--json"])

    recorded = cleanup_dry_run.get("returncode") == 0 and isinstance(scanner_counts.get("tracked_file_count"), int)
    record: dict[str, Any] = {
        "rr_id": RR_ID,
        "status": "workspace_hygiene_recorded" if recorded else "authority_installed_evidence_pending",
        "hygiene_owner": args.hygiene_owner,
        "target_branch": args.target_branch,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "git_state": git_state,
        "clean_git_state_at_capture": git_state.get("status_short") == "",
        "workspace_hygiene_recorded": recorded,
        "safe_cleanup_target_recorded": recorded,
        "tracked_file_audit_inventory_recorded": recorded,
        "reproducible_scanner_counts_recorded": recorded,
        "ignored_artifact_cleanup_dry_run_only": recorded,
        "scanner_counts": scanner_counts,
        "safe_cleanup_dry_run": cleanup_dry_run,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "runtime_kg_implementation_claimed": False,
    }

    _write_json(RECORD, record)
    verification = evaluate(Path("."))
    record["verification"] = verification
    _write_json(RECORD, record)

    raw_dir = EVIDENCE_DIR / "raw"
    _write_json(raw_dir / "record.json", record)
    _write_json(raw_dir / "verification.json", verification)
    _write_json(raw_dir / "workspace_hygiene_audit.json", scanner_counts)
    _write_json(raw_dir / "safe_cleanup_dry_run.json", cleanup_dry_run)
    _write_index(EVIDENCE_DIR / "evidence_index.md", record, verification)

    result = {**verification, "record": record}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"RR-004 evidence valid: {verification['valid']}")

    return 0 if verification["valid"] or not args.require_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
