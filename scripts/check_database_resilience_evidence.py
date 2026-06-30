#!/usr/bin/env python3
"""Validate database resilience evidence for the release PR series."""
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "database_resilience_evidence_2026-05-11.md"

REQUIRED_SNIPPETS = (
    "Database And Resilience Evidence",
    "codex/pr19-database-resilience-evidence",
    "make migration-check database-backup-contract-check database-restore-drill-docs-check database-resilience-env-matrix-check database-backup-integrity-check database-restore-integrity-check",
    "Migration graph check passed with 19 revisions and head `20260510_0200`",
    "python3 scripts/run_database_backup.py --dry-run",
    "python3 scripts/run_database_restore.py --dry-run --target-environment staging",
    "`DATABASE_URL`: missing",
    "`BACKUP_ENCRYPTION_KEY`: missing",
    "`AZURE_STORAGE_CONNECTION_STRING`: missing",
    "`AZURE_STORAGE_CONTAINER`: missing",
    "`target_environment`: allowed for `staging`",
    "No disposable PostgreSQL migration run was executed",
    "No encrypted backup artifact was produced",
    "No restore drill was executed against a separate environment",
    "does not claim production backup readiness",
)


def main() -> int:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    print("Database resilience evidence check")

    if not DOC.exists():
        print(f"- FAIL {DOC.relative_to(REPO_ROOT)}: document missing")
        return 1

    failed = False
    print(f"- PASS {DOC.relative_to(REPO_ROOT)}: document present")
    for snippet in REQUIRED_SNIPPETS:
        if snippet in text:
            print(f"- PASS contains {snippet!r}")
            continue
        print(f"- FAIL missing {snippet!r}")
        failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
