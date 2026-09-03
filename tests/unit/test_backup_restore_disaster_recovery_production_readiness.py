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


@pytest.mark.unit
def test_disaster_recovery_contracts_validation_error_branches() -> None:
    from datetime import datetime, timezone
    from app.modules.disaster_recovery.production_readiness_contracts import (
        BackupFrequency,
        BackupManifestEntry,
        BackupPolicy,
        BackupProviderDecision,
        BackupScope,
        DisasterRecoveryPlan,
        DrillOutcome,
        RecoveryObjective,
        RecoveryTier,
        RestoreDrillEvidence,
        RestoreEnvironment,
        RestoreRunbook,
        default_disaster_recovery_readiness_report,
    )

    # 1. BackupProviderDecision invalid branches
    bad_dec = BackupProviderDecision(
        database_backup_provider="",
        object_backup_provider="",
        backup_storage_provider="",
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/doc.md",
        encrypted_at_rest_required=False,
        encrypted_in_transit_required=False,
        cross_region_copy_required=False,
        immutable_retention_required=False,
    )
    assert len(bad_dec.validate()) == 9

    # 2. BackupPolicy invalid branches
    bad_pol = BackupPolicy(
        scope=BackupScope.DATABASE,
        frequency=BackupFrequency.WEEKLY,
        retention_days=0,
        recovery_tier=RecoveryTier.CRITICAL,
        pitr_enabled=False,
        encrypted=False,
        integrity_check_required=False,
        owner="",
    )
    pol_issues = bad_pol.validate()
    assert "database retention must be positive" in pol_issues
    assert "database critical backups must be hourly or daily" in pol_issues
    assert "database backups require point-in-time recovery" in pol_issues
    assert "database backups must be encrypted" in pol_issues
    assert "database backups require integrity checks" in pol_issues
    assert "database backup owner is required" in pol_issues

    # 3. RecoveryObjective invalid branches
    bad_obj = RecoveryObjective(
        service="",
        recovery_tier=RecoveryTier.CRITICAL,
        rpo_minutes=120,
        rto_minutes=300,
        owner="",
        escalation_route="",
    )
    obj_issues = bad_obj.validate()
    assert "service is required" in obj_issues
    assert "critical services require RPO <= 60 minutes" in obj_issues
    assert "critical services require RTO <= 240 minutes" in obj_issues
    assert "recovery owner is required" in obj_issues
    assert "escalation route is required" in obj_issues

    negative_obj = RecoveryObjective(
        service="svc",
        recovery_tier=RecoveryTier.STANDARD,
        rpo_minutes=-1,
        rto_minutes=-5,
        owner="owner",
        escalation_route="esc",
    )
    assert "RPO cannot be negative" in negative_obj.validate()
    assert "RTO cannot be negative" in negative_obj.validate()

    # 4. BackupManifestEntry invalid branches
    naive_dt = datetime(2026, 1, 1, 0, 0)
    bad_man = BackupManifestEntry(
        manifest_id="",
        scope=BackupScope.DATABASE,
        backup_id="",
        created_at_utc=naive_dt,
        source_environment="",
        storage_location="",
        checksum_sha256="INVALID",
        encrypted=False,
        retention_expires_at_utc=naive_dt,
        contains_personal_information=True,
    )
    man_issues = bad_man.validate()
    assert "manifest_id is required" in man_issues
    assert "backup_id is required" in man_issues
    assert "created_at_utc must be timezone-aware" in man_issues
    assert "source_environment is required" in man_issues
    assert "storage_location is required" in man_issues
    assert "checksum_sha256 must be 64 lowercase hex characters" in man_issues
    assert "backup manifest entry must be encrypted" in man_issues
    assert "retention_expires_at_utc must be timezone-aware" in man_issues

    # 5. RestoreRunbook invalid branches
    bad_run = RestoreRunbook(
        runbook_path="invalid/path.md",
        scope=BackupScope.DATABASE,
        target_environment=RestoreEnvironment.STAGING,
        pre_restore_checks=(),
        restore_steps=(),
        post_restore_validation=(),
        rollback_steps=(),
        owner="",
    )
    assert len(bad_run.validate()) == 6

    # 6. RestoreDrillEvidence invalid branches
    t1 = datetime(2026, 1, 1, 2, 0, tzinfo=timezone.utc)
    t0 = datetime(2026, 1, 1, 1, 0, tzinfo=timezone.utc)
    bad_drill = RestoreDrillEvidence(
        drill_id="",
        scope=BackupScope.DATABASE,
        target_environment=RestoreEnvironment.STAGING,
        started_at_utc=t1,
        completed_at_utc=t0,
        outcome=DrillOutcome.PASS,
        rpo_minutes_observed=-1,
        rto_minutes_observed=-1,
        checksum_verified=False,
        application_smoke_test_passed=False,
        data_integrity_test_passed=False,
        evidence_path="invalid/path.md",
    )
    drill_issues = bad_drill.validate()
    assert "drill_id is required" in drill_issues
    assert "drill completion must be after start" in drill_issues
    assert "observed RPO cannot be negative" in drill_issues
    assert "observed RTO cannot be negative" in drill_issues
    assert "passing restore drill requires checksum verification" in drill_issues
    assert "passing restore drill requires application smoke test" in drill_issues
    assert "passing restore drill requires data integrity test" in drill_issues
    assert "restore drill evidence must live under docs/disaster_recovery/evidence/" in drill_issues

    # 7. DisasterRecoveryPlan invalid branches
    bad_plan = DisasterRecoveryPlan(
        plan_id="",
        incident_commander="",
        technical_lead="",
        privacy_owner="",
        communications_owner="",
        escalation_matrix_path="invalid/path.md",
        business_continuity_path="invalid/path.md",
        annual_test_required=False,
        post_incident_review_required=False,
    )
    assert len(bad_plan.validate()) == 9

    # 8. default_disaster_recovery_readiness_report
    report = default_disaster_recovery_readiness_report()
    assert report["provider_decision_issues"] == []
    assert report["checksum_validation_sample"] is True
    assert report["scope_classification_sample"] == "database"
