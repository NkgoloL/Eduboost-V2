from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.disaster_recovery.production_readiness_contracts import (
    DEFAULT_BACKUP_POLICIES,
    DEFAULT_DR_PLAN,
    DEFAULT_MANIFEST_ENTRY,
    DEFAULT_PROVIDER_DECISION,
    DEFAULT_RECOVERY_OBJECTIVES,
    DEFAULT_RESTORE_DRILL,
    DEFAULT_RESTORE_RUNBOOKS,
    BackupScope,
    classify_backup_scope,
    compute_backup_checksum,
    validate_checksum,
)
from scripts.check_backup_restore_disaster_recovery_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_backup_restore_disaster_recovery_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_backup_restore_disaster_recovery_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_backup_restore_disaster_recovery_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Backup restore disaster recovery production readiness check" in result.stdout


@pytest.mark.unit
def test_disaster_recovery_contracts_validate() -> None:
    assert DEFAULT_PROVIDER_DECISION.validate() == []
    assert [issue for policy in DEFAULT_BACKUP_POLICIES for issue in policy.validate()] == []
    assert [issue for objective in DEFAULT_RECOVERY_OBJECTIVES for issue in objective.validate()] == []
    assert DEFAULT_MANIFEST_ENTRY.validate() == []
    assert [issue for runbook in DEFAULT_RESTORE_RUNBOOKS for issue in runbook.validate()] == []
    assert DEFAULT_RESTORE_DRILL.validate() == []
    assert DEFAULT_DR_PLAN.validate() == []


@pytest.mark.unit
def test_backup_checksum_and_validation() -> None:
    payload = b"eduboost-backup-sample"
    checksum = compute_backup_checksum(payload)

    assert len(checksum) == 64
    assert validate_checksum(payload, checksum)
    assert not validate_checksum(b"tampered", checksum)


@pytest.mark.unit
def test_backup_scope_classification() -> None:
    assert classify_backup_scope("database/postgres/backup.sql") == BackupScope.DATABASE
    assert classify_backup_scope("object-storage/uploads/archive.tar") == BackupScope.OBJECT_STORAGE
    assert classify_backup_scope("audit/logs/export.json") == BackupScope.AUDIT_LOGS
    assert classify_backup_scope("telemetry/export.json") == BackupScope.TELEMETRY_EXPORTS
    assert classify_backup_scope("secrets/metadata.json") == BackupScope.SECRETS_METADATA
    assert classify_backup_scope("config/settings.json") == BackupScope.CONFIGURATION


@pytest.mark.unit
def test_makefile_exposes_backup_restore_disaster_recovery_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backup-restore-disaster-recovery-production-readiness-check:" in text
    assert "scripts/check_backup_restore_disaster_recovery_production_readiness.py" in text
