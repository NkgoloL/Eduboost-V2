#!/usr/bin/env python3
"""Validate production-readiness item 13: backup, restore, and disaster recovery."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.modules.disaster_recovery.production_readiness_contracts import default_disaster_recovery_readiness_report


REQUIRED_FILES = (
    "app/modules/disaster_recovery/__init__.py",
    "app/modules/disaster_recovery/production_readiness_contracts.py",
    "docs/adr/ADR-013-backup-restore-disaster-recovery.md",
    "docs/disaster_recovery/backup_restore_architecture_contract.md",
    "docs/disaster_recovery/backup_policy_retention_contract.md",
    "docs/disaster_recovery/recovery_objectives_contract.md",
    "docs/disaster_recovery/restore_runbook_contract.md",
    "docs/disaster_recovery/restore_drill_evidence_contract.md",
    "docs/disaster_recovery/business_continuity_contract.md",
    "docs/disaster_recovery/dr_escalation_matrix.md",
    "docs/disaster_recovery/runbooks/database_restore.md",
    "docs/disaster_recovery/runbooks/object_storage_restore.md",
    "docs/disaster_recovery/evidence/restore_drill_001.md",
    "docs/backlog/production_readiness/13_backup_restore_and_disaster_recovery.md",
    "tests/unit/test_backup_restore_disaster_recovery_production_readiness.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/disaster_recovery/production_readiness_contracts.py": (
        "class BackupScope",
        "class BackupFrequency",
        "class RestoreEnvironment",
        "class RecoveryTier",
        "class DrillOutcome",
        "BackupProviderDecision",
        "BackupPolicy",
        "RecoveryObjective",
        "BackupManifestEntry",
        "RestoreRunbook",
        "RestoreDrillEvidence",
        "DisasterRecoveryPlan",
        "compute_backup_checksum",
        "validate_checksum",
        "classify_backup_scope",
        "default_disaster_recovery_readiness_report",
    ),
    "docs/adr/ADR-013-backup-restore-disaster-recovery.md": (
        "Backup, Restore, and Disaster Recovery Decision",
        "database point-in-time recovery is required",
        "encrypted backup storage is required",
        "cross-region backup copy is required",
        "immutable retention is required",
        "restore drills are required",
        "RPO and RTO objectives are required",
    ),
    "docs/disaster_recovery/backup_restore_architecture_contract.md": (
        "Backup Restore Architecture Contract",
        "managed database snapshot support",
        "database point-in-time recovery",
        "object storage versioning",
        "encrypted backup vault",
        "backup manifest generation",
        "restore drill evidence",
        "privacy-aware backup access control",
    ),
    "docs/disaster_recovery/backup_policy_retention_contract.md": (
        "Backup Policy and Retention Contract",
        "backup scope",
        "backup frequency",
        "retention days",
        "database backups require point-in-time recovery",
        "critical backups must be hourly or daily",
        "backup owners must be named",
    ),
    "docs/disaster_recovery/recovery_objectives_contract.md": (
        "Recovery Objectives Contract",
        "RPO minutes",
        "RTO minutes",
        "critical services require RPO <= 60 minutes",
        "critical services require RTO <= 240 minutes",
        "escalation route is required",
    ),
    "docs/disaster_recovery/restore_runbook_contract.md": (
        "Restore Runbook Contract",
        "pre-restore checks",
        "restore steps",
        "post-restore validation",
        "rollback steps",
        "checksum verification",
        "application smoke tests",
        "data integrity checks",
    ),
    "docs/disaster_recovery/restore_drill_evidence_contract.md": (
        "Restore Drill Evidence Contract",
        "observed RPO minutes",
        "observed RTO minutes",
        "checksum verified",
        "passing drill requires application smoke test",
        "passing drill requires data integrity test",
    ),
    "docs/disaster_recovery/business_continuity_contract.md": (
        "Business Continuity Contract",
        "incident commander is assigned",
        "privacy owner is assigned",
        "communications owner is assigned",
        "POPIA data subject rights are triaged during outage",
        "post-incident review is required",
    ),
    "docs/backlog/production_readiness/13_backup_restore_and_disaster_recovery.md": (
        "13.6 Repository-side implementation evidence",
        "docs/disaster_recovery/backup_restore_architecture_contract.md",
        "scripts/check_backup_restore_disaster_recovery_production_readiness.py",
        "make backup-restore-disaster-recovery-production-readiness-check",
    ),
    "Makefile": (
        "backup-restore-disaster-recovery-production-readiness-check:",
        "scripts/check_backup_restore_disaster_recovery_production_readiness.py",
    ),
}


@dataclass(frozen=True)
class DisasterRecoveryReadinessResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[DisasterRecoveryReadinessResult]:
    results: list[DisasterRecoveryReadinessResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            DisasterRecoveryReadinessResult(
                rel_path,
                path.exists(),
                "file present" if path.exists() else "file missing",
            )
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(
                DisasterRecoveryReadinessResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    try:
        report = default_disaster_recovery_readiness_report()
        results.extend(
            [
                DisasterRecoveryReadinessResult("disaster_recovery_contracts", report["provider_decision_issues"] == [], "provider decision validates"),
                DisasterRecoveryReadinessResult("disaster_recovery_contracts", report["backup_policy_issues"] == [], "backup policies validate"),
                DisasterRecoveryReadinessResult("disaster_recovery_contracts", report["recovery_objective_issues"] == [], "recovery objectives validate"),
                DisasterRecoveryReadinessResult("disaster_recovery_contracts", report["manifest_entry_issues"] == [], "backup manifest entry validates"),
                DisasterRecoveryReadinessResult("disaster_recovery_contracts", report["restore_runbook_issues"] == [], "restore runbooks validate"),
                DisasterRecoveryReadinessResult("disaster_recovery_contracts", report["restore_drill_issues"] == [], "restore drill evidence validates"),
                DisasterRecoveryReadinessResult("disaster_recovery_contracts", report["dr_plan_issues"] == [], "DR plan validates"),
                DisasterRecoveryReadinessResult("disaster_recovery_contracts", str(report["checksum_sample"]) and report["checksum_validation_sample"] is True, "checksum validation sample passes"),
                DisasterRecoveryReadinessResult("disaster_recovery_contracts", report["scope_classification_sample"] == "database", "backup scope classification sample passes"),
            ]
        )
    except Exception as exc:  # pragma: no cover - defensive CLI output
        results.append(DisasterRecoveryReadinessResult("disaster_recovery_contracts", False, f"contract check failed: {exc}"))

    return results


def main() -> int:
    results = run_checks()
    print("Backup restore disaster recovery production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
