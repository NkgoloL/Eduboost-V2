#!/usr/bin/env python3
"""Aggregate repository-side production-readiness check for backlog item 05."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "docs/backlog/production_readiness/05_database_persistence_migrations_and_performance.md"

REQUIRED_FILES = (
    "docs/database/schema_readiness_contract.md",
    "docs/database/migration_release_discipline_contract.md",
    "docs/database/repository_transaction_performance_contract.md",
    "docs/database/migration_discipline.md",
    "docs/database/schema_integrity.md",
    "docs/reference/repositories.md",
    "scripts/validate_schema_integrity.py",
    "scripts/verify_migration_graph.py",
    "scripts/check_db_repository_evidence.py",
    "scripts/smoke_test_migrations.sh",
    ".github/workflows/migration_check.yml",
    "alembic/env.py",
    "alembic/versions/20260505_1734_add_missing_production_indexes.py",
    "alembic/versions/20260507_1330_database_integrity_constraints.py",
    "alembic/versions/20260507_1200_popia_consent_audit_hardening.py",
    "app/repositories/base.py",
    "app/repositories/learner_repository.py",
    "app/repositories/consent_repository.py",
    "app/repositories/audit_repository.py",
    "app/repositories/diagnostic_repository.py",
    "app/repositories/lesson_repository.py",
    "app/repositories/study_plan_repository.py",
    "app/repositories/gamification_repository.py",
    "tests/unit/test_schema_integrity.py",
    "tests/unit/test_migration_graph.py",
    "tests/unit/test_v2_repository_patterns.py",
    "tests/unit/test_v2_repositories_full.py",
)

CONTENT_REQUIREMENTS = {
    "docs/database/schema_readiness_contract.md": (
        "every production table has explicit primary key evidence",
        "consent status constraints",
        "audit event constraints",
        "active consent partial index",
        "non-revoked session partial index",
        "incomplete job partial index",
        "does not replace `alembic upgrade head`, `alembic check`, staging dry runs",
    ),
    "docs/database/migration_release_discipline_contract.md": (
        "`alembic upgrade head` runs from an empty PostgreSQL database in CI",
        "`alembic check` runs in CI",
        "downgrade and re-upgrade rollback smoke evidence exists in CI",
        "migrations touching learner or guardian data require staging dry run",
        "does not execute production migrations, approve destructive changes",
    ),
    "docs/database/repository_transaction_performance_contract.md": (
        "signup transaction boundary review evidence",
        "repositories do not expose raw ORM objects to API responses",
        "list queries include pagination controls",
        "slow-query logging is required in staging",
        "query latency budgets are defined before production launch",
        "does not perform production load testing, enable production telemetry",
    ),
    "scripts/validate_schema_integrity.py": (
        "REQUIRED_TABLES",
        "REQUIRED_INDEXES",
        "REQUIRED_CONSTRAINTS",
        "missing primary key",
        "missing created_at timestamp",
        "expected at least one foreign key",
        "ix_guardians_email_hash",
        "ix_parental_consents_active_status",
        "idx_audit_events_hash",
        "uq_consent_guardian_learner",
    ),
    "scripts/verify_migration_graph.py": (
        "TIMESTAMPED_NAME",
        "YYYYMMDD_HHMM_<short_description>.py",
        "expected exactly one head revision",
        "expected exactly one base revision",
        "down_revision",
    ),
    ".github/workflows/migration_check.yml": (
        "alembic upgrade head",
        "alembic check",
        "alembic downgrade -2",
        "postgres:16-alpine",
    ),
    "docs/backlog/production_readiness/05_database_persistence_migrations_and_performance.md": (
        "[verify] `P0` Confirm every production table has explicit primary key.",
        "[verify] `P0` Ensure `alembic upgrade head` runs in CI from empty DB.",
        "[verify] `P1` Review transaction boundary for signup.",
        "[verify] `P1` Add repository tests for guardian repository.",
        "[verify] `P1` Add slow-query logging in staging.",
        "docs/database/schema_readiness_contract.md",
        "docs/database/migration_release_discipline_contract.md",
        "docs/database/repository_transaction_performance_contract.md",
        "Verification boundary: these checks prove repository-side readiness evidence",
    ),
}

REPOSITORY_KEYWORDS = (
    "class LearnerRepository",
    "class ConsentRepository",
    "class AuditRepository",
    "class DiagnosticRepository",
    "class LessonRepository",
    "class StudyPlanRepository",
    "class GamificationRepository",
    "limit",
    "order_by",
)

@dataclass(frozen=True)
class Result:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[Result]:
    results: list[Result] = []
    for rel_path in REQUIRED_FILES:
        path = ROOT / rel_path
        results.append(Result(rel_path, path.exists(), "present" if path.exists() else "missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(Result(rel_path, snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))

    repo_dir = ROOT / "app/repositories"
    repo_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in repo_dir.glob("*.py")) if repo_dir.exists() else ""
    for keyword in REPOSITORY_KEYWORDS:
        results.append(Result("app/repositories", keyword in repo_text, f"contains {keyword!r}" if keyword in repo_text else f"missing {keyword!r}"))

    return results


def main() -> int:
    results = run_checks()
    print("Database persistence production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
