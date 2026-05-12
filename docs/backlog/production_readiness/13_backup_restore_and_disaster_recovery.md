# 13. Backup, restore, and disaster recovery

## 13.1 PostgreSQL backups

- [ ] `P0` Enable automated PostgreSQL backups.
- [ ] `P0` Encrypt PostgreSQL backups.
- [ ] `P0` Store backups in separate failure domain.
- [ ] `P0` Define daily retention.
- [ ] `P0` Define weekly retention.
- [ ] `P0` Define monthly retention.
- [ ] `P0` Add backup success metric.
- [ ] `P0` Add backup failure metric.
- [ ] `P0` Add backup failure alert.
- [x] `P0` Document backup configuration. Evidence: `docs/operations/database_backup_contract.md`, `docs/operations/database_backup_command.md`, `docs/operations/persistence_resilience_evidence.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [x] `P0` Add backup runbook. Evidence: `docs/operations/backup_restore_runbook.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [verify] `P1` Add backup integrity verification. Evidence: `scripts/check_database_backup_integrity.py`, `tests/unit/test_database_backup_integrity.py`, `make database-backup-integrity-check`.
- [ ] `P1` Add backup cost monitoring.

## 13.2 Restore tests

- [ ] `P0` Perform restore test into clean environment.
- [ ] `P0` Validate guardian records after restore.
- [ ] `P0` Validate learner records after restore.
- [ ] `P0` Validate consent states after restore.
- [ ] `P0` Validate audit records after restore.
- [ ] `P0` Validate billing states after restore.
- [ ] `P0` Validate diagnostic records after restore.
- [ ] `P0` Validate lesson metadata after restore.
- [ ] `P0` Validate Alembic version after restore.
- [ ] `P0` Record restore duration.
- [x] `P0` Record restore evidence. Evidence: `scripts/generate_database_restore_evidence.py`, `docs/operations/database_restore_evidence.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [ ] `P1` Automate restore test in staging on schedule.

## 13.3 RPO/RTO and DR

- [x] `P0` Define RPO. Evidence: `docs/operations/backup_restore_runbook.md`, `docs/operations/persistence_resilience_evidence.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [x] `P0` Define RTO. Evidence: `docs/operations/backup_restore_runbook.md`, `docs/operations/persistence_resilience_evidence.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [x] `P0` Create disaster recovery documentation. Evidence: `docs/operations/backup_restore_runbook.md`, `docs/operations/database_restore_drill.md`, `docs/operations/persistence_resilience_evidence.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [x] `P0` Add restore runbook. Evidence: `docs/operations/backup_restore_runbook.md`, `docs/operations/database_restore_command.md`, `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [ ] `P0` Add failover runbook.
- [ ] `P0` Add rollback runbook.
- [ ] `P0` Add emergency contacts.
- [ ] `P0` Add disaster declaration criteria.
- [ ] `P1` Run disaster recovery tabletop exercise.
- [ ] `P1` Add post-DR validation checklist.
- [ ] `P2` Add cross-region recovery plan if required.

## 13.4 Redis recoverability

- [verify] `P1` Decide Redis recoverability model. Evidence: `docs/operations/persistence_resilience_evidence.md`; verification gap: executable Redis outage test still required.
- [verify] `P1` Document whether Redis is disposable. Evidence: `docs/operations/persistence_resilience_evidence.md`.
- [verify] `P1` Document token revocation impact if Redis is lost. Evidence: `docs/operations/persistence_resilience_evidence.md`.
- [verify] `P1` Document cache impact if Redis is lost. Evidence: `docs/operations/persistence_resilience_evidence.md`.
- [verify] `P1` Document job status impact if Redis is lost. Evidence: `docs/operations/persistence_resilience_evidence.md`.
- [verify] `P1` Document rate-limit impact if Redis is lost. Evidence: `docs/operations/persistence_resilience_evidence.md`.
- [ ] `P1` Add Redis outage test.
- [ ] `P1` Add degraded-mode behavior for Redis outage.
- [ ] `P2` Add Redis failover test if using managed failover.

---

