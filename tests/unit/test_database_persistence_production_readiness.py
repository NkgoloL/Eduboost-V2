from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_database_persistence_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_database_persistence_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_database_persistence_production_readiness_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_database_persistence_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Database persistence production readiness check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_database_persistence_production_readiness_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "database-persistence-production-readiness-check:" in text
    assert "scripts/check_database_persistence_production_readiness.py" in text


@pytest.mark.unit
def test_database_backlog_05_records_repository_side_evidence() -> None:
    text = (REPO_ROOT / "docs" / "backlog" / "production_readiness" / "05_database_persistence_migrations_and_performance.md").read_text(encoding="utf-8")
    assert "docs/database/schema_readiness_contract.md" in text
    assert "docs/database/migration_release_discipline_contract.md" in text
    assert "docs/database/repository_transaction_performance_contract.md" in text
    assert "Verification boundary: these checks prove repository-side readiness evidence" in text
