#!/usr/bin/env python3
"""Collect RR-005 technical-debt burn-down audit data.

The audit is intentionally inventory-first. It records the current debt shape
without rewriting application code, deleting routes, or mutating migrations.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
from scripts._subprocess import run
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROUTER_GLOBS = (
    "app/api_v2_routers/*.py",
    "app/modules/**/router.py",
    "app/modules/**/*_router.py",
    "app/legacy/**/*router*.py",
)
STALE_COMMENT_PATTERNS = (
    "TODO",
    "FIXME",
    "HACK",
    "temporary",
    "legacy",
    "deprecated",
    "shim",
    "remove after",
)
RUFF_COMMAND = ["ruff", "check", "app", "tests", "scripts", "--statistics"]
RUFF_JSON_COMMAND = ["ruff", "check", "app", "tests", "scripts", "--output-format=json"]


def _run(cmd: list[str], root: Path, timeout: int = 120) -> dict[str, Any]:
    executable = shutil.which(cmd[0])
    if executable is None:
        return {
            "available": False,
            "command": cmd,
            "returncode": None,
            "stdout": "",
            "stderr": f"tool not found on PATH: {cmd[0]}",
        }
    completed = run(
        cmd,
        cwd=root,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return {
        "available": True,
        "command": cmd,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _run_git(args: list[str], root: Path) -> dict[str, Any]:
    completed = run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": ["git", *args],
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _parse_ruff_statistics(stdout: str) -> dict[str, int]:
    # Ruff 0.4.x statistics lines are typically: "402\tE402\tmodule-import-not-at-top-of-file".
    counts: dict[str, int] = {}
    for line in stdout.splitlines():
        match = re.match(r"\s*(\d+)\s+([A-Z]+\d+)\b", line)
        if match:
            counts[match.group(2)] = int(match.group(1))
    return counts


def _parse_ruff_json(stdout: str) -> dict[str, Any]:
    try:
        findings = json.loads(stdout) if stdout.strip() else []
    except json.JSONDecodeError as exc:
        return {"parse_error": str(exc), "finding_count": None, "code_counts": {}, "top_files": []}
    code_counts = Counter(item.get("code") or "UNKNOWN" for item in findings)
    file_counts = Counter(item.get("filename") or "UNKNOWN" for item in findings)
    return {
        "finding_count": len(findings),
        "code_counts": dict(sorted(code_counts.items())),
        "top_files": file_counts.most_common(20),
    }


def collect_ruff_debt(root: Path) -> dict[str, Any]:
    statistics = _run(RUFF_COMMAND, root)
    json_run = _run(RUFF_JSON_COMMAND, root)
    docs_baseline = _read(root / "docs/backlog/ruff_debt.md")
    result: dict[str, Any] = {
        "statistics_command": statistics["command"],
        "json_command": json_run["command"],
        "tool_available": statistics.get("available") is True or json_run.get("available") is True,
        "statistics_returncode": statistics.get("returncode"),
        "json_returncode": json_run.get("returncode"),
        "statistics_stdout": statistics.get("stdout", "")[-12000:],
        "statistics_stderr": statistics.get("stderr", "")[-4000:],
        "json_stderr": json_run.get("stderr", "")[-4000:],
        "statistics_counts": _parse_ruff_statistics(statistics.get("stdout", "")),
        "json_summary": _parse_ruff_json(json_run.get("stdout", "")) if json_run.get("available") else {},
        "docs_baseline_present": bool(docs_baseline.strip()),
        "docs_baseline_mentions_phase_11": "Phase 11" in docs_baseline or "Technical Debt" in docs_baseline,
    }
    # Ruff exits non-zero when findings exist. For RR-005, findings are expected; successful execution means the
    # tool was available and produced debt evidence, not that the debt count is zero.
    result["debt_captured"] = result["tool_available"] and (
        bool(result["statistics_stdout"].strip())
        or isinstance(result.get("json_summary"), dict) and result["json_summary"].get("finding_count") is not None
    )
    result["fallback_to_existing_docs"] = not result["debt_captured"] and result["docs_baseline_present"]
    result["valid"] = result["debt_captured"] or result["fallback_to_existing_docs"]
    return result


def collect_import_linter_exceptions(root: Path) -> dict[str, Any]:
    config = _read(root / ".importlinter")
    ignore_entries: list[str] = []
    in_ignore = False
    for raw_line in config.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped.startswith("ignore_imports"):
            in_ignore = True
            continue
        if stripped.startswith("["):
            in_ignore = False
        if in_ignore and stripped and not stripped.startswith("#"):
            ignore_entries.append(stripped)
    return {
        "config_present": bool(config.strip()),
        "ignore_imports_count": len(ignore_entries),
        "ignore_imports": ignore_entries,
        "valid": bool(config.strip()),
    }


def _router_files(root: Path) -> list[Path]:
    paths: set[Path] = set()
    for pattern in ROUTER_GLOBS:
        paths.update(root.glob(pattern))
    return sorted(path for path in paths if path.is_file())


def collect_stale_route_comments(root: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for path in _router_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped.startswith("#") and "#" not in stripped:
                continue
            for pattern in STALE_COMMENT_PATTERNS:
                if pattern.lower() in stripped.lower():
                    findings.append(
                        {
                            "path": str(path.relative_to(root)),
                            "line": idx,
                            "pattern": pattern,
                            "comment": stripped[:240],
                        }
                    )
                    break
    return {
        "router_file_count": len(_router_files(root)),
        "stale_route_comment_count": len(findings),
        "findings": findings[:200],
        "truncated": len(findings) > 200,
        "valid": True,
    }


def _migration_revision_info(path: Path) -> dict[str, Any]:
    text = _read(path)
    revision = None
    down_revision: str | list[str] | None = None
    try:
        tree = ast.parse(text)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                names = [target.id for target in node.targets if isinstance(target, ast.Name)]
                if "revision" in names:
                    revision = ast.literal_eval(node.value)
                if "down_revision" in names:
                    down_revision = ast.literal_eval(node.value)
    except Exception:
        pass
    return {
        "path": str(path),
        "revision": revision,
        "down_revision": down_revision,
        "is_merge_file": "merge" in path.name.lower() or isinstance(down_revision, (list, tuple)),
        "is_deprecated": "_deprecated" in path.parts,
    }


def collect_migration_history(root: Path) -> dict[str, Any]:
    versions_dir = root / "alembic" / "versions"
    files = sorted(path for path in versions_dir.rglob("*.py") if path.name != "__init__.py")
    info = []
    for path in files:
        row = _migration_revision_info(path)
        row["path"] = str(path.relative_to(root))
        info.append(row)
    return {
        "versions_dir_present": versions_dir.exists(),
        "migration_file_count": len(files),
        "deprecated_migration_file_count": sum(1 for row in info if row["is_deprecated"]),
        "merge_migration_file_count": sum(1 for row in info if row["is_merge_file"]),
        "migrations": info,
        "squash_decision": "defer squash until a dedicated migration-window decision; do not rewrite migration history in RR-005",
        "valid": versions_dir.exists() and bool(files),
    }


def collect_dormant_router_review(root: Path) -> dict[str, Any]:
    inventory_path = root / "docs" / "release" / "dormant_router_inventory.md"
    text = _read(inventory_path)
    routers = re.findall(r"`([^`]+\.py)`", text)
    rows = []
    for router in routers:
        path = root / router
        rows.append({"router": router, "exists": path.exists(), "status": "review required before retirement/archive"})
    return {
        "inventory_present": bool(text.strip()),
        "router_count": len(routers),
        "routers": rows,
        "retirement_decision": "no router retired by this audit-only RR-005 slice; retirement requires call-site proof",
        "valid": bool(text.strip()) and len(routers) > 0,
    }


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    git_branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    git_head = _run_git(["rev-parse", "HEAD"], root)
    git_status = _run_git(["status", "--short"], root)
    ruff = collect_ruff_debt(root)
    import_linter = collect_import_linter_exceptions(root)
    stale_routes = collect_stale_route_comments(root)
    migrations = collect_migration_history(root)
    dormant_routes = collect_dormant_router_review(root)
    checks = {
        "ruff_debt_inventory_collected": ruff["valid"],
        "import_linter_exceptions_registered": import_linter["valid"],
        "stale_route_comments_audited": stale_routes["valid"],
        "migration_history_audited": migrations["valid"],
        "dormant_router_review_recorded": dormant_routes["valid"],
    }
    return {
        "valid": all(checks.values()),
        "checks": checks,
        "git": {
            "branch": git_branch["stdout"] if git_branch["returncode"] == 0 else None,
            "head_sha": git_head["stdout"] if git_head["returncode"] == 0 else None,
            "status_short": git_status["stdout"] if git_status["returncode"] == 0 else None,
        },
        "ruff_debt": ruff,
        "import_linter_exceptions": import_linter,
        "stale_route_comments": stale_routes,
        "migration_history": migrations,
        "dormant_router_review": dormant_routes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", help="optional path to write JSON audit output")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
