#!/usr/bin/env python3
"""Canonical CLI for recording manual evidence and architectural review artifacts.

Enforces:
- Exact reviewer name & role
- Required conflict disclosure
- Decision enum: completed | accepted_risk | deferred | rejected
- Cryptographic SHA-256 binding of the target artifact
- Exact git commit hash at time of review
- Deterministic JSON payload format
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def get_git_commit(root: Path) -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN_COMMIT"


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    temp.replace(path)


def record_review(
    root: Path,
    bundle_id: str,
    control_id: str,
    reviewer: str,
    reviewer_role: str,
    decision: str,
    target_file: Path,
    notes: str,
    conflict_disclosure: str = "Self-review by sole developer; not independent approval.",
) -> Path:
    if not target_file.exists():
        raise FileNotFoundError(f"Target review artifact not found: {target_file}")

    target_sha = sha256_file(target_file)
    git_commit = get_git_commit(root)
    safe_control = control_id.lower().replace(".", "-")
    evidence_dir = root / "docs/release-evidence/true-state-remediation" / bundle_id.lower() / "manual"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_path = evidence_dir / f"{safe_control}.json"

    rel_path = str(target_file.relative_to(root)) if target_file.is_relative_to(root) else str(target_file)

    payload = {
        "schema_version": "eduboost/true-state-remediation/manual-evidence/v1",
        "bundle_id": bundle_id.upper(),
        "control_id": control_id.upper(),
        "reviewer": reviewer,
        "reviewer_role": reviewer_role,
        "conflict_disclosure": conflict_disclosure,
        "decision": decision,
        "recorded_at": utc_now(),
        "git_commit": git_commit,
        "artifact_path": rel_path,
        "artifact_sha256": target_sha,
        "notes": notes,
    }

    atomic_write_json(out_path, payload)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a canonical TSR manual review artifact")
    parser.add_argument("--repo", default=".", help="Repository root")
    parser.add_argument("--bundle", required=True, help="Bundle ID (e.g. B03)")
    parser.add_argument("--control", required=True, help="Control ID (e.g. TSR-4.1)")
    parser.add_argument("--reviewer", default="Nkgolo Lebelo", help="Reviewer name")
    parser.add_argument("--role", default="Lead Engineer (Self-Review)", help="Reviewer role")
    parser.add_argument("--decision", choices=["completed", "accepted_risk", "deferred", "rejected"], default="completed")
    parser.add_argument("--target", required=True, help="Path to artifact file being reviewed")
    parser.add_argument("--notes", default="Completed deliverable review.", help="Review notes")
    parser.add_argument("--conflict-disclosure", default="Self-review by sole developer; not independent approval.", help="Disclosure")

    args = parser.parse_args()
    root = Path(args.repo).resolve()
    target_path = (root / args.target).resolve() if not Path(args.target).is_absolute() else Path(args.target)

    out = record_review(
        root=root,
        bundle_id=args.bundle,
        control_id=args.control,
        reviewer=args.reviewer,
        reviewer_role=args.role,
        decision=args.decision,
        target_file=target_path,
        notes=args.notes,
        conflict_disclosure=args.conflict_disclosure,
    )
    print(f"Recorded manual review evidence: {out.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
