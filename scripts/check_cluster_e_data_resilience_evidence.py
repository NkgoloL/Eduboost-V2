#!/usr/bin/env python3
"""Validate Cluster E data-resilience evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "scripts/check_database_backup_contract.py",
    "scripts/check_database_restore_drill_docs.py",
    "docs/operations/database_backup_contract.md",
    "docs/operations/database_restore_drill.md",
    "tests/unit/test_database_backup_contract.py",
    "tests/unit/test_database_restore_drill_docs.py",
)

CONTENT_REQUIREMENTS = {
    "Makefile": (
        "database-backup-contract-check:",
        "database-restore-drill-docs-check:",
    ),
    "docs/operations/database_backup_contract.md": (
        "Database Backup Contract",
        "backups must be encrypted",
    ),
    "docs/operations/database_restore_drill.md": (
        "Database Restore Drill",
        "Verify consent record counts",
        "Verify audit event counts",
    ),
}


@dataclass(frozen=True)
class ClusterEResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ClusterEResult]:
    results: list[ClusterEResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(ClusterEResult("file", rel_path, path.exists(), "present" if path.exists() else "missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                ClusterEResult(
                    "content",
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = run_checks()
    print("Cluster E data-resilience evidence check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
