#!/usr/bin/env python3
"""Validate database backup manifest integrity evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "docs" / "operations" / "database_backup_manifest.md"

REQUIRED_SNIPPETS = (
    "Database Backup Manifest",
    "Backup artifact ID",
    "Retention days",
    "Encrypted",
    "backup artifact is encrypted",
    "restore drill evidence is linked",
    "make database-backup-dry-run",
)


@dataclass(frozen=True)
class BackupIntegrityResult:
    ok: bool
    detail: str


def run_checks() -> list[BackupIntegrityResult]:
    text = MANIFEST.read_text(encoding="utf-8") if MANIFEST.exists() else ""
    results = [
        BackupIntegrityResult(
            ok=MANIFEST.exists(),
            detail="manifest present" if MANIFEST.exists() else "manifest missing",
        )
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BackupIntegrityResult(
                ok=snippet in text,
                detail=f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    encrypted_line_ok = "| Encrypted | `yes` |" in text or "| Encrypted | `true` |" in text
    results.append(
        BackupIntegrityResult(
            ok=encrypted_line_ok,
            detail="backup manifest marks artifact encrypted" if encrypted_line_ok else "backup manifest does not mark artifact encrypted",
        )
    )

    return results


def main() -> int:
    results = run_checks()
    print("Database backup integrity check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
