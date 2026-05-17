#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "app/api_v2_routers/diagnostics.py"
REPORT = ROOT / "docs/release/diagnostics_data_integrity_repair_report.md"
BLOCKER = ROOT / "docs/release/diagnostics_data_integrity_repair_blockers.md"

IMPORT_LINE = (
    "from app.services.diagnostic_data_integrity import "
    "validate_diagnostic_submission_payload, validate_mastery_update_payload\n"
)
MARKER_SUBMISSION = "# code_691_720_diagnostic_submission_integrity"
MARKER_MASTERY = "# code_691_720_mastery_theta_integrity"


def _write_blocker(message: str) -> None:
    BLOCKER.write_text(
        "\n".join([
            "# Diagnostics Data Integrity Repair Blocker",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            message,
            "",
        ]),
        encoding="utf-8",
    )


def _ensure_import(text: str) -> str:
    if "app.services.diagnostic_data_integrity" in text:
        return text
    lines = text.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith('"""'):
        insert_at = 1
        while insert_at < len(lines) and '"""' not in lines[insert_at]:
            insert_at += 1
        insert_at = min(insert_at + 1, len(lines))
    if insert_at < len(lines) and lines[insert_at].startswith("from __future__"):
        insert_at += 1
    while insert_at < len(lines) and (
        lines[insert_at].startswith("import ") or lines[insert_at].startswith("from ")
    ):
        insert_at += 1
    lines.insert(insert_at, IMPORT_LINE)
    return "".join(lines)


def _args(node: ast.AsyncFunctionDef | ast.FunctionDef) -> list[str]:
    return [arg.arg for arg in node.args.args + node.args.kwonlyargs]


def _payload_arg(args: list[str]) -> str | None:
    for candidate in ("payload", "body", "submission", "request", "answer", "response", "data"):
        if candidate in args:
            return candidate
    for arg in args:
        if arg not in {"db", "session", "current_user", "learner_id", "session_id", "attempt_id"}:
            return arg
    return None


def _is_submission_function(name: str) -> bool:
    name = name.lower()
    return any(token in name for token in ("submit", "answer", "response", "attempt")) and not any(
        token in name for token in ("mastery", "theta", "status", "list", "get_")
    )


def _is_mastery_function(name: str) -> bool:
    name = name.lower()
    return any(token in name for token in ("mastery", "theta", "score")) and any(
        token in name for token in ("update", "submit", "record", "complete")
    )


def main() -> int:
    if not ROUTER.exists():
        _write_blocker("Missing app/api_v2_routers/diagnostics.py")
        print("Diagnostics router missing; wrote blocker.")
        return 1

    source = ROUTER.read_text(encoding="utf-8")
    text = _ensure_import(source)
    tree = ast.parse(text)
    lines = text.splitlines()
    insertions: list[tuple[int, str]] = []
    blockers: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) or node.name.startswith("_"):
            continue

        block = "\n".join(lines[node.lineno - 1:(node.end_lineno or node.lineno)])
        args = _args(node)
        payload = _payload_arg(args)
        if not node.body or payload is None:
            continue

        first = node.body[0]
        indent_match = re.match(r"^(\s*)", lines[first.lineno - 1])
        indent = indent_match.group(1) if indent_match else "    "

        if _is_submission_function(node.name) and MARKER_SUBMISSION not in block:
            snippet = f"{indent}{MARKER_SUBMISSION}\n{indent}validate_diagnostic_submission_payload({payload}, require_items=False)\n"
            insertions.append((first.lineno - 1, snippet))

        if _is_mastery_function(node.name) and MARKER_MASTERY not in block:
            snippet = f"{indent}{MARKER_MASTERY}\n{indent}validate_mastery_update_payload({payload})\n"
            insertions.append((first.lineno - 1, snippet))

    if not insertions and MARKER_SUBMISSION not in text and MARKER_MASTERY not in text:
        blockers.append("No diagnostics submit/answer/response/mastery candidate function with payload-like argument was found.")

    if blockers:
        _write_blocker("\n".join(f"- {item}" for item in blockers))
        for blocker in blockers:
            print(f"BLOCKER: {blocker}")
        return 1

    for line_no, snippet in sorted(insertions, reverse=True):
        lines[line_no:line_no] = snippet.rstrip("\n").splitlines()

    updated = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    ast.parse(updated)

    if updated != source:
        ROUTER.write_text(updated, encoding="utf-8")

    REPORT.write_text(
        "\n".join([
            "# Diagnostics Data Integrity Repair Report",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            "**Status:** implemented",
            "",
            "- Diagnostics router imports `app.services.diagnostic_data_integrity`.",
            "- Submission/answer/response handlers validate diagnostic payload structure.",
            "- Mastery/theta handlers validate finite and bounded theta updates when payload fields are present.",
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
