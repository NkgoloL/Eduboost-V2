#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = [
    Path("app/services/backend_runtime_integration_readiness.py"),
    Path("docs/release/runtime_integration_boundary_policy.md"),
    Path("docs/pr/runtime_integration_pr_template.md"),
    Path("docs/release/backend_runtime_integration_status_rollup.md"),
]

FORBIDDEN_APPROVAL_PATTERNS = [
    "route registration approved",
    "schema migration approved",
    "audit repository deletion approved",
    "consent table merge approved",
    "production db mutation approved",
    "alembic stamp head approved",
]


def main() -> int:
    failures: list[str] = []
    print("Backend runtime integration blocklist check")

    for relative in SCAN_ROOTS:
        path = REPO_ROOT / relative
        if not path.exists():
            print(f"- FAIL [file] {relative}: missing")
            failures.append(f"missing {relative}")
            continue

        text = path.read_text(encoding="utf-8").lower()
        for pattern in FORBIDDEN_APPROVAL_PATTERNS:
            if pattern in text:
                print(f"- FAIL [pattern] {relative}: {pattern}")
                failures.append(f"{relative}: {pattern}")
        print(f"- PASS [file] {relative}: no forbidden approval phrase")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS runtime integration blocklists")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
