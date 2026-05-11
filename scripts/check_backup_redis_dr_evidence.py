#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "docs/disaster_recovery.md",
    "docs/adr/0008-redis-token-revocation.md",
    "docs/operations/backup_restore_runbook.md",
    "docs/operations/database_backup_contract.md",
    "docs/operations/database_restore_drill.md",
    "docs/operations/database_resilience_env_matrix.md",
    "scripts/run_database_backup.py",
    "scripts/run_database_restore.py",
    "scripts/check_database_backup_integrity.py",
    "scripts/check_database_restore_integrity.py",
    "tests/unit/test_database_backup_integrity.py",
    "tests/unit/test_database_restore_integrity.py",
)


@dataclass(frozen=True)
class Result:
    target: str
    ok: bool
    detail: str


def check_all() -> list[Result]:
    return [Result(path, (ROOT / path).exists(), "present" if (ROOT / path).exists() else "missing") for path in REQUIRED]


def main() -> int:
    results = check_all()
    print("Backup/Redis/DR evidence check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
