#!/usr/bin/env python3
"""Validate database backup contract evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/operations/database_backup_contract.md",
)

CONTENT_REQUIREMENTS = {
    "app/core/config.py": (
        "BACKUP_ENCRYPTION_KEY",
        "BACKUP_RETENTION_DAYS",
        "AZURE_STORAGE_CONNECTION_STRING",
        "AZURE_STORAGE_CONTAINER",
    ),
    "docs/operations/database_backup_contract.md": (
        "Database Backup Contract",
        "backups must be encrypted",
        "restore evidence must be attached",
        "BACKUP_ENCRYPTION_KEY",
        "BACKUP_RETENTION_DAYS",
    ),
}


@dataclass(frozen=True)
class BackupContractResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[BackupContractResult]:
    results: list[BackupContractResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            BackupContractResult("file", rel_path, path.exists(), "present" if path.exists() else "missing")
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                BackupContractResult(
                    "content",
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = run_checks()
    print("Database backup contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
