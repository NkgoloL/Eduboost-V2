from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_persistence_resilience_evidence import REQUIRED_FILES, check_all


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_persistence_evidence_required_files_cover_data_resilience_surfaces() -> None:
    assert "scripts/verify_migration_graph.py" in REQUIRED_FILES
    assert "scripts/validate_schema_integrity.py" in REQUIRED_FILES
    assert "scripts/run_database_backup.py" in REQUIRED_FILES
    assert "scripts/run_database_restore.py" in REQUIRED_FILES
    assert "docs/operations/persistence_resilience_evidence.md" in REQUIRED_FILES


@pytest.mark.unit
def test_persistence_resilience_evidence_check_passes_current_repo() -> None:
    failures = [result for result in check_all() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_persistence_resilience_evidence_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_persistence_resilience_evidence.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Persistence resilience evidence check" in result.stdout
