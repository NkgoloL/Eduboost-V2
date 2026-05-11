from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_backup_redis_dr_evidence import REQUIRED, check_all

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_backup_redis_dr_required_files_cover_recoverability() -> None:
    assert "docs/disaster_recovery.md" in REQUIRED
    assert "docs/adr/0008-redis-token-revocation.md" in REQUIRED
    assert "scripts/run_database_restore.py" in REQUIRED


@pytest.mark.unit
def test_backup_redis_dr_evidence_passes() -> None:
    assert [r for r in check_all() if not r.ok] == []


@pytest.mark.unit
def test_backup_redis_dr_cli_passes() -> None:
    result = subprocess.run([sys.executable, "scripts/check_backup_redis_dr_evidence.py"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
