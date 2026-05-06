# Database Backup — EduBoost

This document describes the lightweight automated Postgres backup used by EduBoost.

Script
- `scripts/db_backup.sh` — creates a `pg_dump` custom-format dump, gzips it, and prunes old backups.

Environment
- `DATABASE_URL` (preferred) — full Postgres connection URL
- Or set `PGHOST`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` environment variables
- `BACKUP_DIR` — directory to store backups (default `./backups`)
- `RETENTION_DAYS` — how many days to keep backups (default `7`)

Installation (systemd)
1. Copy `scripts/db_backup.sh` to `/opt/eduboost/scripts/` and `deployment/systemd/db-backup.*` to `/etc/systemd/system/`.
2. Make script executable: `chmod +x /opt/eduboost/scripts/db_backup.sh`.
3. Reload systemd: `systemctl daemon-reload`.
4. Enable and start timer:

```bash
systemctl enable --now db-backup.timer
```

Testing
- Run locally (make sure `pg_dump` is available and env vars set):

```bash
BACKUP_DIR=./tmp-backups RETENTION_DAYS=2 DATABASE_URL="postgres://user:pass@localhost:5432/dbname" bash scripts/db_backup.sh
```

Notes
- The script is intentionally small and POSIX-ish; extend it (S3 upload, encryption, incremental) as needed.
