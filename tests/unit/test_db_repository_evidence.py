from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_db_repository_evidence import REQUIRED, check_all

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_db_repository_required_files_cover_migrations_and_repositories() -> None:
    assert "scripts/verify_migration_graph.py" in REQUIRED
    assert "app/repositories/base.py" in REQUIRED
    assert "tests/unit/test_v2_repository_patterns.py" in REQUIRED


@pytest.mark.unit
def test_db_repository_evidence_passes() -> None:
    assert [r for r in check_all() if not r.ok] == []


@pytest.mark.unit
def test_db_repository_cli_passes() -> None:
    result = subprocess.run([sys.executable, "scripts/check_db_repository_evidence.py"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
