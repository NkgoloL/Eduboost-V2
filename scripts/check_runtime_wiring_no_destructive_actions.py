#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_FILES = [
    Path("app/services/first_consent_runtime_wiring.py"),
    Path("app/services/first_deep_readiness_runtime_wiring.py"),
    Path("docs/release/first_consent_runtime_wiring_pr.md"),
    Path("docs/release/first_deep_readiness_runtime_wiring_pr.md"),
    Path("docs/pr/combined_runtime_wiring_pr_checklist.md"),
]

FORBIDDEN_IMPLEMENTATION_PATTERNS = [
    "drop table",
    "alembic stamp",
    "delete from",
    "merge consent_records",
    "merge parental_consents",
    "route registration change approved",
    "public mutating health",
]


def main() -> int:
    failures: list[str] = []
    print("Runtime wiring destructive-action scan")

    for relative in SCAN_FILES:
        path = REPO_ROOT / relative
        if not path.exists():
            print(f"- FAIL [file] {relative}: missing")
            failures.append(f"missing {relative}")
            continue
        text = path.read_text(encoding="utf-8").lower()
        for pattern in FORBIDDEN_IMPLEMENTATION_PATTERNS:
            if pattern in text and "no " not in text and "does not" not in text and "blocked" not in text:
                print(f"- FAIL [pattern] {relative}: {pattern}")
                failures.append(f"{relative}: {pattern}")
        print(f"- PASS [file] {relative}: no destructive implementation pattern detected")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS runtime wiring destructive-action scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
