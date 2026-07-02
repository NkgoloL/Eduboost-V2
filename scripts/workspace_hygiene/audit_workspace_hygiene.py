#!/usr/bin/env python3
"""Collect reproducible workspace-hygiene scanner counts.

The scanner is intentionally read-only. It prefers git-backed tracked-file
inventory when a .git directory is present, and falls back to filesystem counts
for archive/snapshot validation.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
IGNORED_DIR_NAMES = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "htmlcov", "coverage_html"}
GENERATED_PREFIXES = ("docs/generated/", "docs/release-evidence/")


def _run_git(args: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        return proc.returncode, proc.stdout
    except Exception as exc:  # pragma: no cover - defensive on minimal runners
        return 127, f"{type(exc).__name__}: {exc}"


def _git_tracked_files() -> tuple[list[str], dict[str, Any]]:
    code, output = _run_git(["ls-files"])
    if code == 0:
        files = [line.strip() for line in output.splitlines() if line.strip()]
        return files, {"mode": "git", "returncode": code, "error": None}

    files: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(ROOT).parts
        if any(part in IGNORED_DIR_NAMES for part in rel_parts):
            continue
        files.append(path.relative_to(ROOT).as_posix())
    files.sort()
    return files, {"mode": "filesystem_fallback", "returncode": code, "error": output.strip()}


def _git_ignored_candidates() -> tuple[list[str], dict[str, Any]]:
    code, output = _run_git(["status", "--ignored", "--short"])
    if code != 0:
        return [], {"mode": "unavailable", "returncode": code, "error": output.strip()}
    candidates: list[str] = []
    for line in output.splitlines():
        if not line.startswith("!! "):
            continue
        candidates.append(line[3:].strip())
    candidates.sort()
    return candidates, {"mode": "git_status_ignored", "returncode": code, "error": None}


def _ext(path: str) -> str:
    suffix = Path(path).suffix.lower()
    return suffix if suffix else "[no_ext]"


def collect() -> dict[str, Any]:
    tracked, tracked_source = _git_tracked_files()
    ignored_candidates, ignored_source = _git_ignored_candidates()
    extension_counts = Counter(_ext(path) for path in tracked)
    top_level_counts = Counter(Path(path).parts[0] if Path(path).parts else path for path in tracked)

    docs_files = [p for p in tracked if p.startswith("docs/")]
    script_files = [p for p in tracked if p.startswith("scripts/")]
    test_files = [p for p in tracked if p.startswith("tests/")]
    generated_files = [p for p in tracked if p.startswith(GENERATED_PREFIXES)]

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tracked_file_source": tracked_source,
        "ignored_artifact_source": ignored_source,
        "tracked_file_count": len(tracked),
        "tracked_docs_count": len(docs_files),
        "tracked_scripts_count": len(script_files),
        "tracked_tests_count": len(test_files),
        "tracked_generated_or_evidence_count": len(generated_files),
        "ignored_artifact_candidate_count": len(ignored_candidates),
        "ignored_artifact_candidates_sample": ignored_candidates[:50],
        "extension_counts": dict(sorted(extension_counts.items())),
        "top_level_counts": dict(sorted(top_level_counts.items())),
        "tracked_file_inventory_command": "git ls-files",
        "ignored_artifact_inventory_command": "git status --ignored --short",
        "safe_cleanup_dry_run_command": "python3 scripts/workspace_hygiene/safe_cleanup_ignored_artifacts.py --dry-run --json",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = collect()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        out = ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    if args.json or not args.output:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
