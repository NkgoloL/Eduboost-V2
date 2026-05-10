#!/usr/bin/env python3
"""Validate database restore evidence integrity claims."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = REPO_ROOT / "docs" / "operations" / "database_restore_evidence.md"

REQUIRED_SNIPPETS = (
    "Database Restore Evidence",
    "Backup artifact ID",
    "Target environment",
    "Integrity status",
    "Learner count status",
    "Consent count status",
    "Audit count status",
    "make database-restore-dry-run",
    "make popia-consent-closure-check",
    "Production promotion is blocked",
)


@dataclass(frozen=True)
class RestoreIntegrityResult:
    ok: bool
    detail: str


def run_checks() -> list[RestoreIntegrityResult]:
    text = EVIDENCE.read_text(encoding="utf-8") if EVIDENCE.exists() else ""
    results = [
        RestoreIntegrityResult(
            ok=EVIDENCE.exists(),
            detail="restore evidence present" if EVIDENCE.exists() else "restore evidence missing",
        )
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            RestoreIntegrityResult(
                ok=snippet in text,
                detail=f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    status_fields_present = all(
        label in text
        for label in ("Integrity status", "Learner count status", "Consent count status", "Audit count status")
    )
    results.append(
        RestoreIntegrityResult(
            ok=status_fields_present,
            detail="restore evidence records integrity/count statuses"
            if status_fields_present
            else "restore evidence missing integrity/count statuses",
        )
    )

    return results


def main() -> int:
    results = run_checks()
    print("Database restore integrity check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
