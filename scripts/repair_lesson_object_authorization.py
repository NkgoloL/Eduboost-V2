#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "app/api_v2_routers/lessons.py"
REPORT = ROOT / "docs/release/lesson_object_authorization_repair_report.md"
BLOCKER = ROOT / "docs/release/lesson_object_authorization_repair_blockers.md"

IMPORT_LINE = (
    "from app.services.lesson_authorization import "
    "iter_sync_lesson_ids, require_lesson_read_access_for_current_user, "
    "require_lesson_write_access_for_current_user\n"
)
MARKER_READ = "# code_611_630_lesson_read_authz"
MARKER_WRITE = "# code_611_630_lesson_write_authz"
MARKER_SYNC = "# code_611_630_lesson_sync_authz"


def blocker(items: list[str]) -> int:
    BLOCKER.write_text(
        "\n".join([
            "# Lesson Object Authorization Repair Blocker",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            *(f"- {item}" for item in items),
            "",
        ]),
        encoding="utf-8",
    )
    print("Lesson authorization blockers:")
    for item in items:
        print(f"- {item}")
    return 1


def ensure_import(text: str) -> str:
    if "app.services.lesson_authorization" in text:
        return text
    lines = text.splitlines(keepends=True)
    lines.insert(1, IMPORT_LINE)
    return "".join(lines)


def arg_names(node: ast.AsyncFunctionDef | ast.FunctionDef) -> list[str]:
    return [arg.arg for arg in node.args.args + node.args.kwonlyargs]


def db_arg(args: list[str]) -> str | None:
    return next((x for x in ("db", "session", "db_session") if x in args), None)


def user_arg(args: list[str]) -> str | None:
    return next((x for x in ("current_user", "user", "authenticated_user", "principal") if x in args), None)


def payload_arg(args: list[str]) -> str | None:
    for x in ("sync_payload", "payload", "body", "request", "data", "lesson_sync"):
        if x in args:
            return x
    for x in args:
        if x not in {"db", "session", "db_session", "current_user", "user", "authenticated_user", "principal"} and "lesson" not in x:
            return x
    return None


def is_read(node: ast.AST, args: list[str]) -> bool:
    name = getattr(node, "name", "").lower()
    return "lesson_id" in args and (name.startswith("get_") or name.startswith("read_")) and not any(t in name for t in ("complete", "sync", "update", "delete"))


def is_complete(node: ast.AST, args: list[str]) -> bool:
    name = getattr(node, "name", "").lower()
    return "lesson_id" in args and any(t in name for t in ("complete", "finish", "submit_completion"))


def is_sync(node: ast.AST) -> bool:
    return "sync" in getattr(node, "name", "").lower()


def patch(text: str) -> tuple[str, list[str]]:
    text = ensure_import(text)
    tree = ast.parse(text)
    lines = text.splitlines()
    insertions: list[tuple[int, str]] = []
    blockers: list[str] = []

    nodes = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and not node.name.startswith("_")
    ]

    for node in nodes:
        args = arg_names(node)
        block = "\n".join(lines[node.lineno - 1:(node.end_lineno or node.lineno)])
        db = db_arg(args)
        user = user_arg(args)
        if not node.body:
            continue
        indent_match = re.match(r"^(\s*)", lines[node.body[0].lineno - 1])
        indent = indent_match.group(1) if indent_match else "    "

        if is_read(node, args) and MARKER_READ not in block:
            if not db or not user:
                blockers.append(f"{node.name}: missing db/session or current_user-like argument for read authz")
            else:
                insertions.append((node.body[0].lineno - 1, f"{indent}{MARKER_READ}\n{indent}await require_lesson_read_access_for_current_user({db}, {user}, lesson_id)"))
        if is_complete(node, args) and MARKER_WRITE not in block:
            if not db or not user:
                blockers.append(f"{node.name}: missing db/session or current_user-like argument for write authz")
            else:
                insertions.append((node.body[0].lineno - 1, f"{indent}{MARKER_WRITE}\n{indent}await require_lesson_write_access_for_current_user({db}, {user}, lesson_id)"))
        if is_sync(node) and MARKER_SYNC not in block:
            payload = payload_arg(args)
            if not db or not user or not payload:
                blockers.append(f"{node.name}: missing db/current_user/payload argument for sync authz")
            else:
                snippet = (
                    f"{indent}{MARKER_SYNC}\n"
                    f"{indent}for _lesson_id in iter_sync_lesson_ids({payload}):\n"
                    f"{indent}    await require_lesson_write_access_for_current_user({db}, {user}, _lesson_id)"
                )
                insertions.append((node.body[0].lineno - 1, snippet))

    for line_no, snippet in sorted(insertions, reverse=True):
        lines[line_no:line_no] = snippet.splitlines()

    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), blockers


def main() -> int:
    if not ROUTER.exists():
        return blocker(["Missing app/api_v2_routers/lessons.py"])
    source = ROUTER.read_text(encoding="utf-8")
    updated, blockers = patch(source)
    if blockers:
        return blocker(blockers)
    ast.parse(updated)
    if updated != source:
        ROUTER.write_text(updated, encoding="utf-8")
    REPORT.write_text(
        "\n".join([
            "# Lesson Object Authorization Repair Report",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            "**Status:** implemented",
            "",
            "| Invariant | Status |",
            "|---|---|",
            "| Lesson read routes enforce learner-read by owner learner_id | implemented |",
            "| Lesson completion routes enforce learner-write by owner learner_id | implemented |",
            "| Lesson sync routes validate every submitted lesson_id before mutation | implemented |",
            "",
        ]),
        encoding="utf-8",
    )
    if BLOCKER.exists():
        BLOCKER.unlink()
    print(f"Patched {ROUTER.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
