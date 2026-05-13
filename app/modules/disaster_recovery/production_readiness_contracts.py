"""Repository-verifiable backup, restore, and disaster-recovery readiness contracts.

These contracts do not call a database, object store, cloud provider, or backup
system. They model deterministic repository-side requirements for backup scope,
restore drills, RPO/RTO, retention, encryption, integrity verification, PITR,
DR roles, and incident evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import re
from typing import Mapping


class BackupScope(StrEnum):
    DATABASE = "database"
    OBJECT_STORAGE = "object_storage"
    CONFIGURATION = "configuration"
    SECRETS_METADATA = "secrets_metadata"
    AUDIT_LOGS = "audit_logs"
    TELEMETRY_EXPORTS = "telemetry_exports"


class BackupFrequency(StrEnum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class RestoreEnvironment(StrEnum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    DISASTER_RECOVERY = "disaster_recovery"


class RecoveryTier(StrEnum):
    CRITICAL = "critical"
    IMPORTANT = "important"
    STANDARD = "standard"
    ARCHIVE = "archive"


class DrillOutcome(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class BackupProviderDecision:
    database_backup_provider: str
    object_backup_provider: str
    backup_storage_provider: str
    adr_path: str
    architecture_doc_path: str
    encrypted_at_rest_required: bool
    encrypted_in_transit_required: bool
    cross_region_copy_required: bool
    immutable_retention_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.database_backup_provider:
            issues.append("database backup provider is required")
        if not self.object_backup_provider:
            issues.append("object backup provider is required")
        if not self.backup_storage_provider:
            issues.append("backup storage provider is required")
        if not self.adr_path.startswith("docs/adr/"):
            issues.append("backup provider decision must be documented in docs/adr/")
        if not self.architecture_doc_path.startswith("docs/disaster_recovery/"):
            issues.append("backup architecture must be documented in docs/disaster_recovery/")
        if not self.encrypted_at_rest_required:
            issues.append("backup encryption at rest is required")
        if not self.encrypted_in_transit_required:
            issues.append("backup encryption in transit is required")
        if not self.cross_region_copy_required:
            issues.append("cross-region backup copy is required")
        if not self.immutable_retention_required:
            issues.append("immutable retention is required")
        return issues


@dataclass(frozen=True)
class BackupPolicy:
    scope: BackupScope
    frequency: BackupFrequency
    retention_days: int
    recovery_tier: RecoveryTier
    pitr_enabled: bool
    encrypted: bool
    integrity_check_required: bool
    owner: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.retention_days <= 0:
            issues.append(f"{self.scope.value} retention must be positive")
        if self.recovery_tier == RecoveryTier.CRITICAL and self.frequency not in {BackupFrequency.HOURLY, BackupFrequency.DAILY}:
            issues.append(f"{self.scope.value} critical backups must be hourly or daily")
        if self.scope == BackupScope.DATABASE and not self.pitr_enabled:
            issues.append("database backups require point-in-time recovery")
        if not self.encrypted:
            issues.append(f"{self.scope.value} backups must be encrypted")
        if not self.integrity_check_required:
            issues.append(f"{self.scope.value} backups require integrity checks")
        if not self.owner:
            issues.append(f"{self.scope.value} backup owner is required")
        return issues


@dataclass(frozen=True)
class RecoveryObjective:
    service: str
    recovery_tier: RecoveryTier
    rpo_minutes: int
    rto_minutes: int
    owner: str
    escalation_route: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.service:
            issues.append("service is required")
        if self.rpo_minutes < 0:
            issues.append("RPO cannot be negative")
        if self.rto_minutes < 0:
            issues.append("RTO cannot be negative")
        if self.recovery_tier == RecoveryTier.CRITICAL and self.rpo_minutes > 60:
            issues.append("critical services require RPO <= 60 minutes")
        if self.recovery_tier == RecoveryTier.CRITICAL and self.rto_minutes > 240:
            issues.append("critical services require RTO <= 240 minutes")
        if not self.owner:
            issues.append("recovery owner is required")
        if not self.escalation_route:
            issues.append("escalation route is required")
        return issues


@dataclass(frozen=True)
class BackupManifestEntry:
    manifest_id: str
    scope: BackupScope
    backup_id: str
    created_at_utc: datetime
    source_environment: str
    storage_location: str
    checksum_sha256: str
    encrypted: bool
    retention_expires_at_utc: datetime
    contains_personal_information: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.manifest_id:
            issues.append("manifest_id is required")
        if not self.backup_id:
            issues.append("backup_id is required")
        if self.created_at_utc.tzinfo is None:
            issues.append("created_at_utc must be timezone-aware")
        if not self.source_environment:
            issues.append("source_environment is required")
        if not self.storage_location:
            issues.append("storage_location is required")
        if not re.fullmatch(r"[a-f0-9]{64}", self.checksum_sha256):
            issues.append("checksum_sha256 must be 64 lowercase hex characters")
        if not self.encrypted:
            issues.append("backup manifest entry must be encrypted")
        if self.retention_expires_at_utc.tzinfo is None:
            issues.append("retention_expires_at_utc must be timezone-aware")
        if self.retention_expires_at_utc <= self.created_at_utc:
            issues.append("retention expiry must be after creation time")
        return issues


@dataclass(frozen=True)
class RestoreRunbook:
    runbook_path: str
    scope: BackupScope
    target_environment: RestoreEnvironment
    pre_restore_checks: tuple[str, ...]
    restore_steps: tuple[str, ...]
    post_restore_validation: tuple[str, ...]
    rollback_steps: tuple[str, ...]
    owner: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.runbook_path.startswith("docs/disaster_recovery/runbooks/"):
            issues.append("restore runbook must live under docs/disaster_recovery/runbooks/")
        if not self.pre_restore_checks:
            issues.append("pre-restore checks are required")
        if not self.restore_steps:
            issues.append("restore steps are required")
        if not self.post_restore_validation:
            issues.append("post-restore validation is required")
        if not self.rollback_steps:
            issues.append("rollback steps are required")
        if not self.owner:
            issues.append("restore runbook owner is required")
        return issues


@dataclass(frozen=True)
class RestoreDrillEvidence:
    drill_id: str
    scope: BackupScope
    target_environment: RestoreEnvironment
    started_at_utc: datetime
    completed_at_utc: datetime
    outcome: DrillOutcome
    rpo_minutes_observed: int
    rto_minutes_observed: int
    checksum_verified: bool
    application_smoke_test_passed: bool
    data_integrity_test_passed: bool
    evidence_path: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.drill_id:
            issues.append("drill_id is required")
        if self.started_at_utc.tzinfo is None or self.completed_at_utc.tzinfo is None:
            issues.append("drill timestamps must be timezone-aware")
        if self.completed_at_utc <= self.started_at_utc:
            issues.append("drill completion must be after start")
        if self.rpo_minutes_observed < 0:
            issues.append("observed RPO cannot be negative")
        if self.rto_minutes_observed < 0:
            issues.append("observed RTO cannot be negative")
        if self.outcome == DrillOutcome.PASS and not self.checksum_verified:
            issues.append("passing restore drill requires checksum verification")
        if self.outcome == DrillOutcome.PASS and not self.application_smoke_test_passed:
            issues.append("passing restore drill requires application smoke test")
        if self.outcome == DrillOutcome.PASS and not self.data_integrity_test_passed:
            issues.append("passing restore drill requires data integrity test")
        if not self.evidence_path.startswith("docs/disaster_recovery/evidence/"):
            issues.append("restore drill evidence must live under docs/disaster_recovery/evidence/")
        return issues


@dataclass(frozen=True)
class DisasterRecoveryPlan:
    plan_id: str
    incident_commander: str
    technical_lead: str
    privacy_owner: str
    communications_owner: str
    escalation_matrix_path: str
    business_continuity_path: str
    annual_test_required: bool
    post_incident_review_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.plan_id:
            issues.append("plan_id is required")
        for name, value in {
            "incident_commander": self.incident_commander,
            "technical_lead": self.technical_lead,
            "privacy_owner": self.privacy_owner,
            "communications_owner": self.communications_owner,
        }.items():
            if not value:
                issues.append(f"{name} is required")
        if not self.escalation_matrix_path.startswith("docs/disaster_recovery/"):
            issues.append("escalation matrix must be documented in docs/disaster_recovery/")
        if not self.business_continuity_path.startswith("docs/disaster_recovery/"):
            issues.append("business continuity plan must be documented in docs/disaster_recovery/")
        if not self.annual_test_required:
            issues.append("annual DR test is required")
        if not self.post_incident_review_required:
            issues.append("post-incident review is required")
        return issues


def compute_backup_checksum(payload: bytes) -> str:
    """Compute deterministic SHA-256 checksum for backup-manifest evidence."""

    return hashlib.sha256(payload).hexdigest()


def validate_checksum(payload: bytes, expected_sha256: str) -> bool:
    """Validate backup payload checksum without exposing payload contents."""

    return compute_backup_checksum(payload) == expected_sha256


def classify_backup_scope(path: str) -> BackupScope:
    """Classify a backup artifact path into a supported scope."""

    lowered = path.lower()
    if "database" in lowered or "postgres" in lowered or "sql" in lowered:
        return BackupScope.DATABASE
    if "object" in lowered or "uploads" in lowered or "storage" in lowered:
        return BackupScope.OBJECT_STORAGE
    if "audit" in lowered:
        return BackupScope.AUDIT_LOGS
    if "telemetry" in lowered:
        return BackupScope.TELEMETRY_EXPORTS
    if "secret" in lowered:
        return BackupScope.SECRETS_METADATA
    return BackupScope.CONFIGURATION


DEFAULT_PROVIDER_DECISION = BackupProviderDecision(
    database_backup_provider="managed_postgres_snapshot_and_wal_archive",
    object_backup_provider="versioned_object_storage_replication",
    backup_storage_provider="encrypted_cross_region_backup_vault",
    adr_path="docs/adr/ADR-013-backup-restore-disaster-recovery.md",
    architecture_doc_path="docs/disaster_recovery/backup_restore_architecture_contract.md",
    encrypted_at_rest_required=True,
    encrypted_in_transit_required=True,
    cross_region_copy_required=True,
    immutable_retention_required=True,
)

DEFAULT_BACKUP_POLICIES = (
    BackupPolicy(BackupScope.DATABASE, BackupFrequency.HOURLY, 35, RecoveryTier.CRITICAL, True, True, True, "database-owner"),
    BackupPolicy(BackupScope.OBJECT_STORAGE, BackupFrequency.DAILY, 35, RecoveryTier.IMPORTANT, False, True, True, "platform-owner"),
    BackupPolicy(BackupScope.CONFIGURATION, BackupFrequency.DAILY, 90, RecoveryTier.IMPORTANT, False, True, True, "platform-owner"),
    BackupPolicy(BackupScope.SECRETS_METADATA, BackupFrequency.DAILY, 90, RecoveryTier.CRITICAL, False, True, True, "security-owner"),
    BackupPolicy(BackupScope.AUDIT_LOGS, BackupFrequency.DAILY, 365, RecoveryTier.CRITICAL, False, True, True, "privacy-owner"),
)

DEFAULT_RECOVERY_OBJECTIVES = (
    RecoveryObjective("api", RecoveryTier.CRITICAL, 60, 240, "engineering", "release-owner"),
    RecoveryObjective("database", RecoveryTier.CRITICAL, 30, 240, "database-owner", "engineering"),
    RecoveryObjective("object-storage", RecoveryTier.IMPORTANT, 240, 480, "platform-owner", "engineering"),
    RecoveryObjective("audit-logs", RecoveryTier.CRITICAL, 60, 240, "privacy-owner", "privacy"),
)

_SAMPLE_CREATED = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
_SAMPLE_EXPIRES = datetime(2026, 2, 5, 0, 0, tzinfo=timezone.utc)
_SAMPLE_COMPLETED = datetime(2026, 1, 1, 1, 0, tzinfo=timezone.utc)
_SAMPLE_CHECKSUM = compute_backup_checksum(b"eduboost-backup-sample")

DEFAULT_MANIFEST_ENTRY = BackupManifestEntry(
    manifest_id="backup-manifest-001",
    scope=BackupScope.DATABASE,
    backup_id="database-backup-001",
    created_at_utc=_SAMPLE_CREATED,
    source_environment="staging",
    storage_location="backup-vault://staging/database/database-backup-001",
    checksum_sha256=_SAMPLE_CHECKSUM,
    encrypted=True,
    retention_expires_at_utc=_SAMPLE_EXPIRES,
    contains_personal_information=True,
)

DEFAULT_RESTORE_RUNBOOKS = (
    RestoreRunbook(
        "docs/disaster_recovery/runbooks/database_restore.md",
        BackupScope.DATABASE,
        RestoreEnvironment.STAGING,
        ("confirm target environment is isolated", "confirm backup manifest checksum"),
        ("restore database snapshot", "apply WAL archive to target timestamp"),
        ("run migration status check", "run application smoke tests", "run data integrity checks"),
        ("discard target database", "restore previous staging snapshot"),
        "database-owner",
    ),
    RestoreRunbook(
        "docs/disaster_recovery/runbooks/object_storage_restore.md",
        BackupScope.OBJECT_STORAGE,
        RestoreEnvironment.STAGING,
        ("confirm bucket namespace", "confirm object manifest checksum"),
        ("restore versioned objects", "verify object metadata"),
        ("sample object access", "run learner asset smoke test"),
        ("remove restored objects", "restore previous object pointers"),
        "platform-owner",
    ),
)

DEFAULT_RESTORE_DRILL = RestoreDrillEvidence(
    drill_id="restore-drill-001",
    scope=BackupScope.DATABASE,
    target_environment=RestoreEnvironment.STAGING,
    started_at_utc=_SAMPLE_CREATED,
    completed_at_utc=_SAMPLE_COMPLETED,
    outcome=DrillOutcome.PASS,
    rpo_minutes_observed=15,
    rto_minutes_observed=60,
    checksum_verified=True,
    application_smoke_test_passed=True,
    data_integrity_test_passed=True,
    evidence_path="docs/disaster_recovery/evidence/restore_drill_001.md",
)

DEFAULT_DR_PLAN = DisasterRecoveryPlan(
    plan_id="dr-plan-001",
    incident_commander="release-owner",
    technical_lead="engineering",
    privacy_owner="privacy",
    communications_owner="support",
    escalation_matrix_path="docs/disaster_recovery/dr_escalation_matrix.md",
    business_continuity_path="docs/disaster_recovery/business_continuity_contract.md",
    annual_test_required=True,
    post_incident_review_required=True,
)


def default_disaster_recovery_readiness_report() -> dict[str, object]:
    """Return deterministic backup, restore, and disaster-recovery readiness evidence."""

    payload = b"eduboost-backup-sample"
    return {
        "provider_decision_issues": DEFAULT_PROVIDER_DECISION.validate(),
        "backup_policy_issues": [issue for policy in DEFAULT_BACKUP_POLICIES for issue in policy.validate()],
        "recovery_objective_issues": [issue for objective in DEFAULT_RECOVERY_OBJECTIVES for issue in objective.validate()],
        "manifest_entry_issues": DEFAULT_MANIFEST_ENTRY.validate(),
        "restore_runbook_issues": [issue for runbook in DEFAULT_RESTORE_RUNBOOKS for issue in runbook.validate()],
        "restore_drill_issues": DEFAULT_RESTORE_DRILL.validate(),
        "dr_plan_issues": DEFAULT_DR_PLAN.validate(),
        "checksum_sample": compute_backup_checksum(payload),
        "checksum_validation_sample": validate_checksum(payload, DEFAULT_MANIFEST_ENTRY.checksum_sha256),
        "scope_classification_sample": classify_backup_scope("database/postgres/backup.sql").value,
    }
