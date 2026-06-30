# DB Backup / Restore / Rollback Evidence Status

Generated at: `2026-05-23T15:26:24Z`
Commit: `d3e97cde34d4cfe5ab81d4d39aeb646300e59e1c`

**Status:** `db-backup-restore-rollback-not-accepted`
**Source DB:** ``
**Restore DB:** ``
**Dump label:** ``
**Dump SHA256:** ``
**Dump size bytes:** `0`
**Source table count:** `None`
**Restore table count:** `None`
**Source Alembic:** ``
**Restore Alembic:** ``
**Run ID:** ``
**Run URL:** ``

## Key table counts

| Table | Source | Restore |
|---|---:|---:|

## Key count mismatches

- None

## Backup output excerpt

```text

```

## Restore output excerpt

```text

```

## Blockers

- DB_ROLLBACK_SOURCE_DATABASE_URL is missing, placeholder, local, or invalid
- DB_ROLLBACK_RESTORE_DATABASE_URL is missing, placeholder, local, or invalid

## No false-closure rules

- DB-ROLLBACK-001 closes only in `DB_ROLLBACK_ACCEPT=1` mode.
- Source and restore database URLs must differ.
- Restore target must be disposable/staging, not production.
- Dump is not uploaded; checksum and status evidence only are persisted.
- Source and restore table count, Alembic version, and key table counts must match.
- A successful GitHub Actions run matching current commit is required.
- This proof does not close JWT, ARQ, DIAG-SCORE, AUDIT-WRITE, approvals, frontend runtime, image/SBOM, security scans, or beta release.
