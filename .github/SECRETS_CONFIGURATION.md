# GitHub Actions Secret Configuration for db-backup-restore-rollback-evidence

## Required Secrets

Add these secrets to your repository at:
https://github.com/NkgoloL/Eduboost-V2/settings/secrets/actions

### 1. DB_ROLLBACK_SOURCE_DATABASE_URL
**Purpose:** Connection string to your production/actual Supabase database

**Format:**
```
postgresql://postgres:[YOUR_DB_PASSWORD]@db.ezjzbvybbwynqpqnbrdt.supabase.co:5432/postgres
```

**How to get your database password:**
1. Go to https://supabase.com/dashboard/project/ezjzbvybbwynqpqnbrdt
2. Navigate to **Database** → **Connection**
3. Click **"Show password"** or **"Connection string (Direct)"**
4. Copy the password from the connection string

**Example (replace PASSWORD_HERE):**
```
postgresql://postgres:PASSWORD_HERE@db.ezjzbvybbwynqpqnbrdt.supabase.co:5432/postgres?sslmode=require
```

### 2. DB_ROLLBACK_RESTORE_DATABASE_URL
**Purpose:** Connection string to the disposable restore database

**Value:**
```
postgresql://postgres:RestorePass123@localhost:5433/postgres
```

**Note:** This is already configured in the workflow file to use the service container. It creates a disposable PostgreSQL 17 container on port 5433 for testing the restore.

---

## Configuration Notes

### Why two different URLs?
- **Source URL:** Points to your actual Supabase database with real data
- **Restore URL:** Points to a disposable container for safe testing

### SSL Mode
The workflow script automatically appends `?sslmode=require` for Supabase URLs if not already present.

### Security
- These secrets are encrypted in GitHub's storage
- Only visible in workflow runs (not in logs by default)
- Never commit connection strings to your repository

---

## How to Test

After adding the secrets, trigger the workflow:

1. Go to: https://github.com/NkgoloL/Eduboost-V2/actions/workflows/db-backup-restore-rollback-evidence.yml
2. Click **"Run workflow"**
3. Set **run_drill** to `true` to actually test the backup/restore
4. Set **run_drill** to `false` for a dry-run (just validation)

---

## Expected Output

When successful, the workflow will:
1. Connect to your source database
3. Run `pg_dump` to create a backup
4. Restore to the disposable database
5. Verify data integrity (table counts, Alembic version)
6. Generate status reports in `docs/release/`

---

## Troubleshooting

If the workflow fails:

1. **Invalid database URL:** Check that you didn't copy placeholder values
2. **Authentication failed:** Verify your database password is correct
3. **Source = Restore:** Make sure the two URLs point to different databases
4. **Missing secrets:** Check that the secret names match exactly (case-sensitive)

---

## Current Supabase Project Details

**Project Name:** Eduboost
**Project ID:** ezjzbvybbwynqpqnbrdt
**Region:** eu-west-1
**Database Version:** PostgreSQL 17.6.1.121
**Database Host:** db.ezjzbvybbwynqpqnbrdt.supabase.co

---

## Alternative Database Variables

The script also checks these alternative variable names (in order):

**For Source:**
- `BACKUP_SOURCE_DATABASE_URL`
- `STAGING_DATABASE_URL`
- `DATABASE_URL`

**For Restore:**
- `RESTORE_DATABASE_URL`
- `DISPOSABLE_DATABASE_URL`

Use `DB_ROLLBACK_*` as the primary naming convention for clarity.
