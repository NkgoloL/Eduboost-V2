from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.run_database_backup import REQUIRED_ENV, render_plan, validate_environment


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_database_backup_preflight_requires_expected_environment() -> None:
    assert "DATABASE_URL" in REQUIRED_ENV
    assert "BACKUP_ENCRYPTION_KEY" in REQUIRED_ENV
    assert "AZURE_STORAGE_CONNECTION_STRING" in REQUIRED_ENV
    assert "AZURE_STORAGE_CONTAINER" in REQUIRED_ENV


@pytest.mark.unit
def test_database_backup_preflight_reports_missing_values() -> None:
    results = validate_environment({})

    assert results
    assert all(not result.ok for result in results)


@pytest.mark.unit
def test_database_backup_preflight_reports_present_values() -> None:
    env = {name: f"value-for-{name}" for name in REQUIRED_ENV}
    results = validate_environment(env)

    assert all(result.ok for result in results)


@pytest.mark.unit
def test_database_backup_plan_documents_dry_run_behavior() -> None:
    plan = render_plan("artifacts/backups", dry_run=True)

    assert "Database Backup Plan" in plan
    assert "dry-run" in plan
    assert "CI must use `--dry-run`" in plan


@pytest.mark.unit
def test_database_backup_dry_run_cli_passes_without_env() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_database_backup.py", "--dry-run"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Database backup preflight" in result.stdout
    assert "Database Backup Plan" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_database_backup_dry_run() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "database-backup-dry-run:" in text
    assert "scripts/run_database_backup.py --dry-run" in text
