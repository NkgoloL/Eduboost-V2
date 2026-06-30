#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    Path("docs/release/backend_consolidation_execution_packet.md"): [
        "implementation sequencing only",
        "Explicitly forbidden",
        "alembic stamp head",
    ],
    Path("docs/release/audit_canonicalization_implementation_checklist.md"): [
        "AuditRepositoryCompatAdapter",
        "Legacy data retained",
        "Deletion postponed",
    ],
    Path("docs/release/consent_runtime_repair_checklist.md"): [
        "ConsentService",
        "POPIADataRightsService",
        "Read/write authz preserved",
    ],
    Path("docs/release/schema_drift_db_execution_checklist.md"): [
        "make migration-evidence-capture",
        "make schema-drift-check-db",
        "no blind stamp",
    ],
    Path("docs/release/deep_readiness_implementation_checklist.md"): [
        "read-only",
        "internal/admin only",
        "must not write to the DB",
    ],
}

FORBIDDEN = [
    "deletion approved",
    "fresh start accepted",
    "discard history",
    "stamp head as repair approved",
]


def main() -> int:
    failures: list[str] = []
    print("Backend consolidation execution packet check")

    for path, needles in REQUIRED.items():
        full = REPO_ROOT / path
        if full.exists():
            print(f"- PASS [file] {path}: present")
        else:
            print(f"- FAIL [file] {path}: missing")
            failures.append(f"missing {path}")
            continue

        text = full.read_text(encoding="utf-8")
        lower = text.lower()
        for needle in needles:
            if needle in text:
                print(f"- PASS [content] {path}: contains {needle!r}")
            else:
                print(f"- FAIL [content] {path}: missing {needle!r}")
                failures.append(f"{path} missing {needle!r}")
        for phrase in FORBIDDEN:
            if phrase in lower:
                print(f"- FAIL [guard] {path}: premature phrase {phrase!r}")
                failures.append(f"{path} has premature phrase {phrase!r}")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS backend consolidation execution packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
