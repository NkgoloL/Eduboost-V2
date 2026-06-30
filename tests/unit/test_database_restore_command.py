from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.run_database_restore import (
    REQUIRED_ENV,
    build_restore_command,
    render_plan,
    validate_environment,
    validate_restore_confirmation,
    validate_target_environment,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_database_restore_preflight_requires_expected_environment() -> None:
    assert "DATABASE_URL" in REQUIRED_ENV
    assert "BACKUP_ENCRYPTION_KEY" in REQUIRED_ENV


@pytest.mark.unit
def test_database_restore_preflight_reports_missing_values() -> None:
    results = validate_environment({})

    assert results
    assert all(not result.ok for result in results)


@pytest.mark.unit
def test_database_restore_blocks_production_target_by_default() -> None:
    result = validate_target_environment("production", allow_production=False)

    assert not result.ok
    assert "requires --allow-production-target" in result.detail


@pytest.mark.unit
def test_database_restore_allows_staging_target() -> None:
    result = validate_target_environment("staging", allow_production=False)

    assert result.ok


@pytest.mark.unit
def test_database_restore_plan_documents_integrity_checks() -> None:
    plan = render_plan("backup.dump", "staging", dry_run=True)

    assert "Database Restore Plan" in plan
    assert "verify learner record counts" in plan
    assert "verify consent record counts" in plan
    assert "verify audit event counts" in plan


@pytest.mark.unit
def test_database_restore_dry_run_cli_passes_for_staging_without_env() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_database_restore.py", "--dry-run", "--target-environment", "staging"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Database restore preflight" in result.stdout
    assert "Database Restore Plan" in result.stdout


@pytest.mark.unit
def test_database_restore_dry_run_cli_blocks_production_target() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_database_restore.py", "--dry-run", "--target-environment", "production"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "production restore requires --allow-production-target" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_database_restore_dry_run() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "database-restore-dry-run:" in text
    assert "scripts/run_database_restore.py --dry-run --target-environment staging" in text


@pytest.mark.unit
def test_database_restore_requires_confirm_for_production_execution() -> None:
    result = validate_restore_confirmation("production", confirm_restore=False)

    assert not result.ok
    assert "--confirm-restore" in result.detail


@pytest.mark.unit
def test_database_restore_builds_pg_restore_and_psql_commands() -> None:
    dump_command = build_restore_command("postgresql://user:pass@db/app", "backup.dump")
    sql_command = build_restore_command("postgresql://user:pass@db/app", "backup.sql")

    assert dump_command[:5] == ["pg_restore", "--clean", "--if-exists", "--no-owner", "--no-privileges"]
    assert "backup.dump" in dump_command
    assert sql_command[:4] == ["psql", "postgresql://user:pass@db/app", "--set", "ON_ERROR_STOP=on"]
    assert sql_command[-1] == "backup.sql"
