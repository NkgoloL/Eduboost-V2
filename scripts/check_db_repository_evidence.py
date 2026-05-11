#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "scripts/verify_migration_graph.py",
    "scripts/validate_schema_integrity.py",
    "scripts/smoke_test_migrations.sh",
    "docs/database/migration_discipline.md",
    "docs/database/schema_integrity.md",
    "docs/reference/repositories.md",
    "app/repositories/base.py",
    "app/repositories/learner_repository.py",
    "app/repositories/consent_repository.py",
    "app/repositories/audit_repository.py",
    "tests/unit/test_migration_graph.py",
    "tests/unit/test_schema_integrity.py",
    "tests/unit/test_v2_repository_patterns.py",
    "tests/unit/test_v2_repositories_full.py",
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
    print("DB/repository evidence check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
