#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "app/api_v2_routers/lessons.py"
REPORT = ROOT / "docs/release/lesson_object_authorization_repair_report.md"
MARKER_READ = "# code_611_630_lesson_read_authz"
MARKER_WRITE = "# code_611_630_lesson_write_authz"
MARKER_SYNC = "# code_611_630_lesson_sync_authz"


def args(node):
    return [arg.arg for arg in node.args.args + node.args.kwonlyargs]


def block(src, node):
    lines = src.splitlines()
    return "\n".join(lines[node.lineno - 1:(node.end_lineno or node.lineno)])


def main() -> int:
    failures: list[str] = []
    print("Lesson object authorization repair check")
    src = ROUTER.read_text(encoding="utf-8")
    tree = ast.parse(src)

    if "app.services.lesson_authorization" in src:
        print("- PASS helper import present")
    else:
        print("- FAIL helper import missing")
        failures.append("helper import")

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name.startswith("_"):
            continue
        a = args(node)
        b = block(src, node)
        name = node.name.lower()
        if "lesson_id" in a and (name.startswith("get_") or name.startswith("read_")) and "complete" not in name:
            if MARKER_READ not in b or "require_lesson_read_access_for_current_user" not in b:
                print(f"- FAIL {node.name}: read authz missing")
                failures.append(f"{node.name} read")
            else:
                print(f"- PASS {node.name}: read authz present")
        if "lesson_id" in a and any(t in name for t in ("complete", "finish", "submit_completion")):
            if MARKER_WRITE not in b or "require_lesson_write_access_for_current_user" not in b:
                print(f"- FAIL {node.name}: write authz missing")
                failures.append(f"{node.name} write")
            else:
                print(f"- PASS {node.name}: write authz present")
        if "sync" in name:
            if MARKER_SYNC not in b or "iter_sync_lesson_ids" not in b or "require_lesson_write_access_for_current_user" not in b:
                print(f"- FAIL {node.name}: sync authz missing")
                failures.append(f"{node.name} sync")
            else:
                print(f"- PASS {node.name}: sync authz present")

    if REPORT.exists():
        print("- PASS repair report exists")
    else:
        print("- FAIL repair report missing")
        failures.append("report")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS lesson object authorization repair")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
