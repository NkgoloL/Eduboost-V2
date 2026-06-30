# 13. Backup, restore, and disaster recovery

## 13.1 PostgreSQL backups

- [verify] `P0` Enable automated PostgreSQL backups.
- [verify] `P0` Encrypt PostgreSQL backups.
- [verify] `P0` Store backups in separate failure domain.
- [verify] `P0` Define daily retention.
- [verify] `P0` Define weekly retention.
- [verify] `P0` Define monthly retention.
- [verify] `P0` Add backup success metric.
- [verify] `P0` Add backup failure metric.
- [verify] `P0` Add backup failure alert.
- [x] `P0` Document backup configuration. Evidence: `docs/operations/database_backup_contract.md`, `docs/operations/database_backup_command.md`, `docs/operations/persistence_resilience_evidence.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [x] `P0` Add backup runbook. Evidence: `docs/operations/backup_restore_runbook.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [verify] `P1` Add backup integrity verification. Evidence: `scripts/check_database_backup_integrity.py`, `tests/unit/test_database_backup_integrity.py`, `make database-backup-integrity-check`.
- [verify] `P1` Add backup cost monitoring.

## 13.2 Restore tests

- [verify] `P0` Perform restore test into clean environment.
- [verify] `P0` Validate guardian records after restore.
- [verify] `P0` Validate learner records after restore.
- [verify] `P0` Validate consent states after restore.
- [verify] `P0` Validate audit records after restore.
- [verify] `P0` Validate billing states after restore.
- [verify] `P0` Validate diagnostic records after restore.
- [verify] `P0` Validate lesson metadata after restore.
- [verify] `P0` Validate Alembic version after restore.
- [verify] `P0` Record restore duration.
- [x] `P0` Record restore evidence. Evidence: `scripts/generate_database_restore_evidence.py`, `docs/operations/database_restore_evidence.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [verify] `P1` Automate restore test in staging on schedule.

## 13.3 RPO/RTO and DR

- [x] `P0` Define RPO. Evidence: `docs/operations/backup_restore_runbook.md`, `docs/operations/persistence_resilience_evidence.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [x] `P0` Define RTO. Evidence: `docs/operations/backup_restore_runbook.md`, `docs/operations/persistence_resilience_evidence.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [x] `P0` Create disaster recovery documentation. Evidence: `docs/operations/backup_restore_runbook.md`, `docs/operations/database_restore_drill.md`, `docs/operations/persistence_resilience_evidence.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [x] `P0` Add restore runbook. Evidence: `docs/operations/backup_restore_runbook.md`, `docs/operations/database_restore_command.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [verify] `P0` Add failover runbook.
- [verify] `P0` Add rollback runbook.
- [verify] `P0` Add emergency contacts.
- [verify] `P0` Add disaster declaration criteria.
- [verify] `P1` Run disaster recovery tabletop exercise.
- [verify] `P1` Add post-DR validation checklist.
- [verify] `P2` Add cross-region recovery plan if required.

## 13.4 Redis recoverability

- [verify] `P1` Decide Redis recoverability model. Evidence: `docs/operations/persistence_resilience_evidence.md`; verification gap: executable Redis outage test still required.
- [verify] `P1` Document whether Redis is disposable. Evidence: `docs/operations/persistence_resilience_evidence.md`.
- [verify] `P1` Document token revocation impact if Redis is lost. Evidence: `docs/operations/persistence_resilience_evidence.md`.
- [verify] `P1` Document cache impact if Redis is lost. Evidence: `docs/operations/persistence_resilience_evidence.md`.
- [verify] `P1` Document job status impact if Redis is lost. Evidence: `docs/operations/persistence_resilience_evidence.md`.
- [verify] `P1` Document rate-limit impact if Redis is lost. Evidence: `docs/operations/persistence_resilience_evidence.md`.
- [verify] `P1` Add Redis outage test.
- [verify] `P1` Add degraded-mode behavior for Redis outage.
- [verify] `P2` Add Redis failover test if using managed failover.

---



## 13.6 Repository-side implementation evidence

- [verify] Backup/restore/DR decision is documented in `docs/adr/ADR-013-backup-restore-disaster-recovery.md`.
- [verify] Backup restore architecture is documented in `docs/disaster_recovery/backup_restore_architecture_contract.md`.
- [verify] Backup policy and retention controls are documented in `docs/disaster_recovery/backup_policy_retention_contract.md`.
- [verify] Recovery objectives are documented in `docs/disaster_recovery/recovery_objectives_contract.md`.
- [verify] Restore runbook controls are documented in `docs/disaster_recovery/restore_runbook_contract.md`.
- [verify] Restore drill evidence controls are documented in `docs/disaster_recovery/restore_drill_evidence_contract.md`.
- [verify] Business continuity and escalation controls are documented in `docs/disaster_recovery/business_continuity_contract.md` and `docs/disaster_recovery/dr_escalation_matrix.md`.
- [verify] Database and object-storage restore runbooks exist under `docs/disaster_recovery/runbooks/`.
- [verify] Restore drill evidence template exists under `docs/disaster_recovery/evidence/`.
- [verify] Deterministic repository contracts live in `app/modules/disaster_recovery/production_readiness_contracts.py`.
- [verify] Repository validation is provided by `scripts/check_backup_restore_disaster_recovery_production_readiness.py`.
- [verify] Domain validation wrapper is provided by `scripts/check_domain_13_backup_restore_disaster_recovery_evidence.py`.
- [verify] Unit coverage is provided by `tests/unit/test_backup_restore_disaster_recovery_production_readiness.py`.
- [verify] Make target is `make backup-restore-disaster-recovery-production-readiness-check`.

### Verification boundary

This implementation provides repository-side backup, restore, retention, RPO/RTO, restore drill, business continuity, and disaster recovery readiness evidence. It does not create backups, restore data, provision backup storage, execute DR drills, or authorize production launch.
