#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    Path("docs/release/backend_data_retention_approval_update.md"),
    Path("docs/release/runtime_wiring_approval_checklist.md"),
    Path("docs/release/backend_runtime_enablement_packet.md"),
    Path("docs/pr/backend_runtime_wiring_pr_template.md"),
]
FORBIDDEN_APPROVALS = [
    "audit_logs deletion: approved",
    "audit history discard: approved",
    "consent history deletion: approved",
    "alembic stamp head: approved",
    "production database mutation approved",
]


def main() -> int:
    failures: list[str] = []
    print("Backend destructive action blocklist check")

    for relative in DOCS:
        path = REPO_ROOT / relative
        if not path.exists():
            print(f"- FAIL [file] {relative}: missing")
            failures.append(f"missing {relative}")
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_APPROVALS:
            if phrase in text:
                print(f"- FAIL [blocklist] {relative}: {phrase}")
                failures.append(f"{relative}: {phrase}")
        print(f"- PASS [file] {relative}: no forbidden approval phrase")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS destructive action blocklist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
