#!/usr/bin/env python3
"""Verify the canonical EduBoost V2 codemap suite and its source-coverage manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REQUIRED_TRACE_TOKENS = (
    "## Trace ID:",
    "**Title:**",
    "**Description:**",
    "**Motivation:**",
    "**Details:**",
    "**Trace text diagram:**",
    "**Location ID:",
    "### AI Guide:",
)
LOCATION_RE = re.compile(r"\*\*Path:LineNumber:\*\*\s+([^:\n]+):(\d+)")
ABSOLUTE_RE = re.compile(r"^(?:/|[A-Za-z]:[\\/])")
EXCLUDED_PARTS = {
    ".git", "node_modules", ".next", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".venv", "venv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--codemap-dir", type=Path, default=None)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def resolve_path(repo_root: Path, codemap_dir: Path, relative: str) -> Path:
    if relative.startswith("docs/codemaps/"):
        return codemap_dir / Path(relative).name
    return repo_root / relative


def is_inventory_file(path: Path, repo_root: Path, policy: dict) -> bool:
    try:
        rel = path.relative_to(repo_root).as_posix()
    except ValueError:
        return False
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    if rel.startswith("docs/codemaps/"):
        return False
    if rel.startswith("docs/archive/codemaps_pre_"):
        return False
    if path.name in set(policy["special_names"]):
        return True
    return path.suffix.lower() in set(policy["included_text_extensions"])


def rebuild_inventory(repo_root: Path, codemap_dir: Path, policy: dict) -> set[str]:
    found: set[str] = set()
    for root_name in policy["roots"]:
        root = repo_root / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and is_inventory_file(path, repo_root, policy):
                found.add(path.relative_to(repo_root).as_posix())
    for root_file in policy["root_files"]:
        path = repo_root / root_file
        if path.is_file():
            found.add(root_file)
    for path in codemap_dir.iterdir():
        if path.is_file() and (
            path.name in set(policy["special_names"])
            or path.suffix.lower() in set(policy["included_text_extensions"])
        ):
            found.add(f"docs/codemaps/{path.name}")
    return found


def verify(repo_root: Path, codemap_dir: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    manifest_path = codemap_dir / "codemap_coverage_manifest.json"
    if not manifest_path.is_file():
        return {"valid": False, "errors": [f"missing manifest: {manifest_path}"], "warnings": []}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    codemaps = manifest.get("codemaps", [])
    expected_ids = {item["id"] for item in codemaps}
    expected_docs = {Path(item["path"]).name for item in codemaps}

    for required in ("README.md", "SUPERSESSION_MAP.md", "CODEMAP_COVERAGE_REPORT.md"):
        if not (codemap_dir / required).is_file():
            errors.append(f"missing required codemap artifact: {required}")

    for name in sorted(expected_docs):
        path = codemap_dir / name
        if not path.is_file():
            errors.append(f"missing canonical codemap: {name}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        trace_count = text.count("## Trace ID:")
        if trace_count < 1:
            errors.append(f"{name}: no traces")
        for token in REQUIRED_TRACE_TOKENS:
            if token not in text:
                errors.append(f"{name}: missing required token {token}")
        if re.search(r"\*\*Path:LineNumber:\*\*\s+(?:/|[A-Za-z]:[\\/])", text):
            errors.append(f"{name}: contains absolute source path")
        locations = LOCATION_RE.findall(text)
        if not locations:
            errors.append(f"{name}: no parsable Path:LineNumber references")
        for relative, line_text in locations:
            relative = relative.strip()
            if ABSOLUTE_RE.match(relative):
                errors.append(f"{name}: absolute reference {relative}")
                continue
            source = resolve_path(repo_root, codemap_dir, relative)
            if not source.is_file():
                errors.append(f"{name}: missing source reference {relative}")
                continue
            line_no = int(line_text)
            total = len(source.read_text(encoding="utf-8", errors="replace").splitlines())
            if line_no < 1 or line_no > max(total, 1):
                errors.append(f"{name}: line {line_no} outside {relative} (1..{max(total,1)})")

    assignments = manifest.get("assignments", [])
    assignment_paths = [item.get("path") for item in assignments]
    duplicate_paths = sorted(path for path, count in Counter(assignment_paths).items() if count > 1)
    if duplicate_paths:
        errors.append(f"duplicate primary assignments: {duplicate_paths[:20]}")

    for item in assignments:
        relative = item.get("path", "")
        owner = item.get("primary_owner")
        if not relative:
            errors.append("manifest assignment with empty path")
            continue
        if owner not in expected_ids:
            errors.append(f"{relative}: unknown owner {owner}")
        source = resolve_path(repo_root, codemap_dir, relative)
        if not source.is_file():
            errors.append(f"manifest path missing: {relative}")

    policy = manifest.get("inventory_policy", {})
    rebuilt = rebuild_inventory(repo_root, codemap_dir, policy)
    declared = set(assignment_paths)
    missing_assignments = sorted(rebuilt - declared)
    stale_assignments = sorted(declared - rebuilt)
    if missing_assignments:
        errors.append(f"unassigned maintained files ({len(missing_assignments)}): {missing_assignments[:30]}")
    if stale_assignments:
        errors.append(f"stale manifest paths ({len(stale_assignments)}): {stale_assignments[:30]}")

    summary = manifest.get("summary", {})
    if summary.get("unassigned_files") != 0:
        errors.append("manifest summary does not declare zero unassigned files")
    if summary.get("duplicate_primary_assignments") != 0:
        errors.append("manifest summary does not declare zero duplicate primary assignments")
    if summary.get("inventoried_files") != len(assignments):
        errors.append("manifest inventoried_files does not match assignment count")

    actual_counts = Counter(item["primary_owner"] for item in assignments)
    for item in codemaps:
        if item.get("assigned_file_count") != actual_counts[item["id"]]:
            errors.append(
                f"{item['id']}: assigned_file_count {item.get('assigned_file_count')} "
                f"!= actual {actual_counts[item['id']]}"
            )

    return {
        "valid": not errors,
        "canonical_codemaps": len(expected_docs),
        "execution_traces": sum(
            (codemap_dir / name).read_text(encoding="utf-8", errors="replace").count("## Trace ID:")
            for name in expected_docs
            if (codemap_dir / name).is_file()
        ),
        "source_references": sum(
            len(LOCATION_RE.findall((codemap_dir / name).read_text(encoding="utf-8", errors="replace")))
            for name in expected_docs
            if (codemap_dir / name).is_file()
        ),
        "manifest_assignments": len(assignments),
        "reconstructed_inventory": len(rebuilt),
        "unassigned_files": len(missing_assignments),
        "stale_manifest_paths": len(stale_assignments),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    codemap_dir = (args.codemap_dir or (repo_root / "docs" / "codemaps")).resolve()
    result = verify(repo_root, codemap_dir)
    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"valid: {str(result['valid']).lower()}")
        for key in (
            "canonical_codemaps", "execution_traces", "source_references",
            "manifest_assignments", "reconstructed_inventory",
            "unassigned_files", "stale_manifest_paths",
        ):
            if key in result:
                print(f"{key}: {result[key]}")
        for warning in result.get("warnings", []):
            print(f"warning: {warning}")
        for error in result.get("errors", []):
            print(f"error: {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
