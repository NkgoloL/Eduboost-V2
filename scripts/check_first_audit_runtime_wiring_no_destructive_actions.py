#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_FILES = [
    Path("app/services/first_audit_runtime_wiring.py"),
    Path("docs/release/first_audit_runtime_wiring_pr.md"),
    Path("docs/pr/first_audit_runtime_wiring_pr_checklist.md"),
]

FORBIDDEN_PATTERNS = [
    "drop table",
    "alembic stamp",
    "delete repository",
    "delete audit_logs",
    "merge consent_records",
    "merge parental_consents",
    "production database mutation",
]


def main() -> int:
    failures: list[str] = []
    print("First audit runtime wiring destructive-action guard")

    for relative in SCAN_FILES:
        path = REPO_ROOT / relative
        if not path.exists():
            print(f"- FAIL [file] {relative}: missing")
            failures.append(f"missing {relative}")
            continue
        text = path.read_text(encoding="utf-8").lower()
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text and "does not" not in text and "no " not in text:
                print(f"- FAIL [pattern] {relative}: {pattern}")
                failures.append(f"{relative}: {pattern}")
        print(f"- PASS [file] {relative}: no destructive implementation pattern detected")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS destructive-action guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
