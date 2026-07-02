#!/usr/bin/env python3
"""Dry-run-first cleanup helper for ignored workspace artifacts.

Default behavior is safe and read-only. Actual deletion requires both --execute
and --confirm-delete-ignored-artifacts and delegates to git clean -fdX.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def _run(args: list[str]) -> dict[str, Any]:
    try:
        proc = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        return {"command": args, "returncode": proc.returncode, "output": proc.stdout}
    except Exception as exc:  # pragma: no cover - defensive
        return {"command": args, "returncode": 127, "output": f"{type(exc).__name__}: {exc}"}


def cleanup(dry_run: bool, execute: bool, confirmed: bool) -> dict[str, Any]:
    if execute and not confirmed:
        return {
            "valid": False,
            "executed": False,
            "dry_run": dry_run,
            "error": "actual cleanup requires --confirm-delete-ignored-artifacts",
        }
    if execute:
        command = ["git", "clean", "-fdX"]
    else:
        command = ["git", "clean", "-ndX"]
    result = _run(command)
    candidates = [line.strip() for line in result["output"].splitlines() if line.strip()]
    return {
        "valid": result["returncode"] == 0,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "executed": execute,
        "dry_run": not execute,
        "command": command,
        "returncode": result["returncode"],
        "candidate_count": len(candidates),
        "candidates": candidates[:200],
        "raw_output": result["output"],
        "safety_boundary": "default dry-run only; actual deletion requires explicit execute plus confirmation flag",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-delete-ignored-artifacts", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = cleanup(dry_run=not args.execute, execute=args.execute, confirmed=args.confirm_delete_ignored_artifacts)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid" if result.get("valid") else "invalid")
        print(f"candidate_count: {result.get('candidate_count', 0)}")
        if result.get("error"):
            print(f"ERROR: {result['error']}")
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
