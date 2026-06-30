# Data Resilience Evidence Index

## Cluster E Closure

- `docs/operations/CLUSTER_E_CLOSURE.md`
- `docs/operations/cluster_e_closure_check.md`
- `.github/workflows/cluster-e-data-resilience.yml`

## Backup Evidence

- `docs/operations/database_backup_contract.md`
- `docs/operations/database_backup_command.md`
- `docs/operations/database_backup_manifest.md`
- `docs/operations/database_backup_integrity_check.md`

## Restore Evidence

- `docs/operations/database_restore_drill.md`
- `docs/operations/database_restore_command.md`
- `docs/operations/database_restore_evidence.md`
- `docs/operations/database_restore_integrity_check.md`

## Restore Readiness

- `docs/operations/database_resilience_env_matrix.md`
- `docs/operations/production_restore_approval.md`

## Required Commands

```bash
make database-backup-contract-check
make database-restore-drill-docs-check
make database-backup-dry-run
make database-restore-dry-run
make database-backup-manifest
make database-restore-evidence
make database-backup-integrity-check
make database-restore-integrity-check
make database-resilience-env-matrix-check
make production-restore-approval-check
make cluster-e-data-resilience-check
make cluster-e-closure-check
```
