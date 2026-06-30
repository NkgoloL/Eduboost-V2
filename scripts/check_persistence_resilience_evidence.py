#!/usr/bin/env python3
"""Validate persistence, migration, backup, restore, and DR evidence wiring."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/database/migration_discipline.md",
    "docs/database/schema_integrity.md",
    "docs/operations/backup_restore_runbook.md",
    "docs/operations/database_backup_contract.md",
    "docs/operations/database_restore_drill.md",
    "docs/operations/database_backup_integrity_check.md",
    "docs/operations/database_restore_integrity_check.md",
    "docs/operations/database_resilience_env_matrix.md",
    "docs/operations/production_restore_approval.md",
    "docs/operations/persistence_resilience_evidence.md",
    "scripts/verify_migration_graph.py",
    "scripts/validate_schema_integrity.py",
    "scripts/smoke_test_migrations.sh",
    "scripts/run_database_backup.py",
    "scripts/run_database_restore.py",
    "scripts/generate_database_backup_manifest.py",
    "scripts/generate_database_restore_evidence.py",
    "scripts/check_database_backup_integrity.py",
    "scripts/check_database_restore_integrity.py",
    "tests/unit/test_persistence_resilience_evidence.py",
)

CONTENT_REQUIREMENTS = {
    "docs/operations/persistence_resilience_evidence.md": (
        "Migration Discipline",
        "Schema Integrity",
        "Backup Dry Run",
        "Restore Dry Run",
        "RPO/RTO",
        "Redis Recoverability",
        "make persistence-resilience-check",
        "Verification Gaps",
    ),
    "Makefile": (
        "migration-check",
        "schema-integrity",
        "migration-smoke",
        "database-backup-dry-run",
        "database-restore-dry-run",
        "database-backup-integrity-check",
        "database-restore-integrity-check",
        "persistence-resilience-check",
    ),
}


@dataclass(frozen=True)
class EvidenceResult:
    target: str
    ok: bool
    detail: str


def check_all() -> list[EvidenceResult]:
    results: list[EvidenceResult] = []
    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(EvidenceResult(rel_path, path.exists(), "present" if path.exists() else "missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                EvidenceResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )
    return results


def main() -> int:
    results = check_all()
    print("Persistence resilience evidence check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
