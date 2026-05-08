# Database Backup — EduBoost

This document describes the lightweight automated Postgres backup used by EduBoost.

Script
- `scripts/db_backup.sh` — creates a `pg_dump` custom-format dump, gzips it, and prunes old backups.

Environment
- `DATABASE_URL` (preferred) — full Postgres connection URL
- Or set `PGHOST`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` environment variables
- `BACKUP_DIR` — directory to store backups (default `./backups`)
- `RETENTION_DAYS` — how many days to keep backups (default `7`)

Encryption
- `ENCRYPTION_TOOL` — set to `age` or `gpg` to enable encryption (default empty = no encryption)
- If `ENCRYPTION_TOOL=age` set `AGE_RECIPIENTS` to a comma- or space-separated list of age recipient public keys (e.g. `age1... age1...`). Example usage:

```bash
ENCRYPTION_TOOL=age AGE_RECIPIENTS="age1..." DATABASE_URL="$DATABASE_URL" bash scripts/db_backup.sh
```

- If `ENCRYPTION_TOOL=gpg` set `GPG_RECIPIENT` to the recipient (email or keyid). Example:

```bash
ENCRYPTION_TOOL=gpg GPG_RECIPIENT="backup@yourorg.example" DATABASE_URL="$DATABASE_URL" bash scripts/db_backup.sh
```

- `KEEP_PLAINTEXT=true` will retain the gzipped dump alongside the encrypted artifact (disabled by default).

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
