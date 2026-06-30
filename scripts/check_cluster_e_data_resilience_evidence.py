#!/usr/bin/env python3
"""Validate Cluster E data-resilience evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "tests/unit/test_cluster_e_release_gate_wiring.py",
    "tests/unit/test_data_resilience_evidence_index.py",
    "docs/operations/data_resilience_evidence_index.md",
    "tests/unit/test_production_restore_approval.py",
    "tests/unit/test_database_resilience_env_matrix.py",
    "docs/operations/production_restore_approval.md",
    "docs/operations/database_resilience_env_matrix.md",
    "scripts/check_production_restore_approval.py",
    "scripts/check_database_resilience_env_matrix.py",
    "tests/unit/test_cluster_e_closure_report.py",
    "tests/unit/test_cluster_e_closure_check.py",
    "docs/operations/CLUSTER_E_CLOSURE.md",
    "docs/operations/cluster_e_closure_check.md",
    "scripts/check_cluster_e_closure.py",
    "tests/unit/test_database_restore_integrity.py",
    "tests/unit/test_database_backup_integrity.py",
    "docs/operations/database_restore_integrity_check.md",
    "docs/operations/database_backup_integrity_check.md",
    "scripts/check_database_restore_integrity.py",
    "scripts/check_database_backup_integrity.py",
    "tests/unit/test_generate_database_restore_evidence.py",
    "tests/unit/test_generate_database_backup_manifest.py",
    "docs/operations/database_restore_evidence.md",
    "docs/operations/database_backup_manifest.md",
    "scripts/generate_database_restore_evidence.py",
    "scripts/generate_database_backup_manifest.py",
    "tests/unit/test_database_restore_command.py",
    "tests/unit/test_database_backup_command.py",
    "docs/operations/database_restore_command.md",
    "docs/operations/database_backup_command.md",
    "scripts/run_database_restore.py",
    "scripts/run_database_backup.py",
    "scripts/check_database_backup_contract.py",
    "scripts/check_database_restore_drill_docs.py",
    "docs/operations/database_backup_contract.md",
    "docs/operations/database_restore_drill.md",
    "tests/unit/test_database_backup_contract.py",
    "tests/unit/test_database_restore_drill_docs.py",
)

CONTENT_REQUIREMENTS = {
    "docs/operations/project_evidence_index.md": (
        "docs/operations/data_resilience_evidence_index.md",
        "make cluster-e-closure-check",
    ),
    "docs/operations/staging_release_gate.md": (
        "make cluster-e-closure-check",
        "docs/operations/CLUSTER_E_CLOSURE.md",
    ),
    "docs/operations/release_evidence_manifest.md": (
        "Cluster E data resilience",
        "make cluster-e-closure-check",
    ),
    "docs/operations/data_resilience_evidence_index.md": (
        "Data Resilience Evidence Index",
        "Cluster E Closure",
        "Backup Evidence",
        "Restore Evidence",
        "make cluster-e-closure-check",
    ),
    "docs/operations/production_restore_approval.md": (
        "Production Restore Approval Guard",
        "production restore requires `--allow-production-target`",
    ),
    "docs/operations/database_resilience_env_matrix.md": (
        "Database Resilience Environment Matrix",
        "production restore requires explicit approval",
    ),
    "docs/operations/CLUSTER_E_CLOSURE.md": (
        "Cluster E Data Resilience Closure",
        "make cluster-e-closure-check",
        "evidence scaffold",
    ),
    "docs/operations/cluster_e_closure_check.md": (
        "Cluster E Closure Check",
        "make cluster-e-closure-check",
    ),
    "docs/operations/database_restore_integrity_check.md": (
        "Database Restore Integrity Check",
        "make database-restore-integrity-check",
    ),
    "docs/operations/database_backup_integrity_check.md": (
        "Database Backup Integrity Check",
        "make database-backup-integrity-check",
    ),
    "scripts/generate_database_restore_evidence.py": (
        "RestoreEvidenceInput",
        "Consent count status",
        "Audit count status",
    ),
    "scripts/generate_database_backup_manifest.py": (
        "BackupManifestInput",
        "backup artifact is encrypted",
    ),
    "docs/operations/database_restore_evidence.md": (
        "Database Restore Evidence",
        "Production promotion is blocked",
    ),
    "docs/operations/database_backup_manifest.md": (
        "Database Backup Manifest",
        "backup artifact is encrypted",
    ),
    "scripts/run_database_restore.py": (
        "validate_target_environment",
        "--allow-production-target",
        "--dry-run",
    ),
    "scripts/run_database_backup.py": (
        "REQUIRED_ENV",
        "BACKUP_ENCRYPTION_KEY",
        "--dry-run",
    ),
    "docs/operations/database_restore_command.md": (
        "Database Restore Command",
        "make database-restore-dry-run",
        "production target is blocked",
    ),
    "docs/operations/database_backup_command.md": (
        "Database Backup Command",
        "make database-backup-dry-run",
    ),
    "Makefile": (
        "database-backup-contract-check:",
        "database-restore-drill-docs-check:",
        "database-backup-dry-run:",
        "database-restore-dry-run:",
        "database-backup-manifest:",
        "database-restore-evidence:",
        "database-backup-integrity-check:",
        "database-restore-integrity-check:",
        "cluster-e-closure-check:",
        "database-resilience-env-matrix-check:",
        "production-restore-approval-check:",
    ),
    "docs/operations/database_backup_contract.md": (
        "Database Backup Contract",
        "backups must be encrypted",
    ),
    "docs/operations/database_restore_drill.md": (
        "Database Restore Drill",
        "Verify consent record counts",
        "Verify audit event counts",
    ),
}


@dataclass(frozen=True)
class ClusterEResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ClusterEResult]:
    results: list[ClusterEResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(ClusterEResult("file", rel_path, path.exists(), "present" if path.exists() else "missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                ClusterEResult(
                    "content",
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = run_checks()
    print("Cluster E data-resilience evidence check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
