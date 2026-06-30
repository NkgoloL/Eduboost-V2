# DB Backup/Restore/Rollback Drill — Troubleshooting & Runbook

This document records every step taken to produce a successful run of `scripts/db_backup_restore_rollback_evidence.py --run-drill` against Supabase Postgres (server 17.x) using containerized clients and a disposable restore database. It is intentionally verbose so future engineers can reproduce the process and understand all troubleshooting performed.

Table of contents
- Background and objectives
- Environment and constraints
- Files involved
- High-level approach
- Detailed chronological troubleshooting steps (with commands and explanations)
- Final working commands
- Artifacts produced and where to find them
- Recommendations and notes

Background and objectives
-------------------------
Goal: Produce verifiable evidence that a database backup can be taken from a Supabase Postgres instance and restored into a disposable restore database, producing matching smoke checks and artifact evidence files.

Constraints:
- Supabase-managed schemas (auth, storage, extensions) are not writable or owned by the project; attempts to restore full dumps into target Supabase-managed projects fail due to permission errors.
- Must use PostgreSQL client tools matching server major version (server is 17.x). Local machine had `pg_dump`/`pg_restore` v16.
- The evidence script (`scripts/db_backup_restore_rollback_evidence.py`) expects `git` to be available to determine current commit unless `DB_ROLLBACK_COMMIT_SHA` is provided.

Environment and tools
---------------------
- Host OS: Linux (Ubuntu on WSL in my case)
- Docker installed for containerized clients
- Python 3.11 used inside container for running the evidence script
- Postgres: server 17 (Supabase managed)

Files involved
--------------
- `scripts/db_backup_restore_rollback_evidence.py` — main orchestration script
- `.env.local` — local environment (contains SUPABASE/DB credentials)
- `db_rollback_test.dump` — working dump file created earlier at repo root
- `docs/release/db_backup_restore_rollback_evidence_status.json` and `.md` — evidence outputs

High-level approach
-------------------
1. Use a `postgres:17` container (or install `postgresql-client-17` inside a python container) to ensure client tools match server major version.
2. Avoid trying to restore Supabase-managed schemas/objects. Restrict restore to `--schema=public` or restore into a disposable Postgres instance.
3. Ensure `git` is available in the runtime environment or pass `DB_ROLLBACK_COMMIT_SHA` to the script to avoid requiring `git`.
4. Run the evidence script with `--run-drill` to create a dump, run pg_restore into the disposable DB, and write evidence JSON + MD.

Detailed chronological troubleshooting steps
-------------------------------------------
Note: the commands are verbatim as executed. Replace sensitive values with placeholders where relevant.

1) Initial attempt (local) — version mismatch and permission errors

- Problem: local `pg_dump`/`pg_restore` were v16 while Supabase is v17.
- Command used to check version:

```bash
pg_dump --version
pg_restore --version
```

- Observed: `pg_restore` reported `unsupported version (1.16) in file header` when attempting to restore a dump created by a PG17 client.

2) Use `postgres:17` container for pg tools

- Rationale: avoid client/server incompatibility by using PG 17 client binaries.

```bash
docker run --rm -v "$PWD":/work -w /work postgres:17 bash -lc \
  "pg_restore --no-owner --no-acl --schema=public --dbname '$DB_ROLLBACK_RESTORE_DATABASE_URL' /work/db_rollback_test.dump"
```

- Result: The `--schema=public` restore still failed when target DB already had objects; many "relation already exists" and ownership errors were printed. This confirmed we must either restore into a fresh DB or drop/create `public` before restoring.

3) Evidence script initial run inside `python:3.11-slim` container

- The evidence script depends on `pg_dump`, `pg_restore`, and `git` (for current commit). When the container didn't have `git`, the run failed obtaining current commit.

- Command used (first attempt installed git only after detection):

```bash
# run from repo root
DB_ROLLBACK_SOURCE_DATABASE_URL='postgresql://...source...' \
DB_ROLLBACK_RESTORE_DATABASE_URL='postgresql://...restore...' \
  docker run --rm -v "$PWD":/work -w /work python:3.11-slim bash -lc "\
    set -x; if ! command -v git >/dev/null 2>&1; then apt-get update -y && apt-get install -y git; fi; \
    apt-get install -y postgresql-client-17 gcc libpq-dev || true; \
    pip install --no-cache-dir psycopg2-binary || true; \
    python scripts/db_backup_restore_rollback_evidence.py --run-drill"
```

- Observed: the container lacked `pg_dump`/`pg_restore` initially, then installing `postgresql-client-17` added them. However, restoring into the target Supabase restore DB failed with permission/owner errors for Supabase-managed schemas.

4) Diagnosis of Supabase-managed schema permission errors

- Errors included messages such as:
  - "must be owner of table ..."
  - "Non-superuser owned event trigger must execute a non-superuser owned function"
  - "extension \"supabase_vault\" is not available"

- Explanation: Supabase-hosted clusters restrict operations for managed extensions/schemas. You cannot re-create or change ownership of these objects as a non-superuser. Therefore, full-restore into a Supabase project is not possible.

5) Workarounds considered

- Option 1: Restore only `public` schema using `--schema=public`.
- Option 2: Restore into a fresh, disposable Postgres instance (not Supabase) to fully validate restore capability.
- Option 3: Drop and recreate `public` on the restore DB (destructive — only acceptable on disposable targets).

6) Implemented approach: disposable Postgres container + allow passing `pg_restore` extra args

- I chose to run the drill into a temporary `postgres:17` container (disposable), and added a small patch to the evidence script to support passing extra `pg_restore` args via environment variable `DB_ROLLBACK_PG_RESTORE_ARGS` (e.g. `--schema=public`). This made the script flexible without changing its default behavior.

Patch applied to `scripts/db_backup_restore_rollback_evidence.py` (key change):

- Added `import shlex`.
- Built the `pg_restore` command as follows (pseudocode):

```py
extra_args = env('DB_ROLLBACK_PG_RESTORE_ARGS')
extras = shlex.split(extra_args) if extra_args else []
cmd = ["pg_restore", "--clean", "--if-exists", "--no-owner", "--no-acl"] + extras + ["--dbname", dst_url, str(dump_path)]
restore = run(cmd)
```

- This allows: `DB_ROLLBACK_PG_RESTORE_ARGS='--schema=public'` to be passed into the container.

7) Creating a disposable Postgres 17 container and running the drill there

- Commands used (automated in a script run):

```bash
# create network
docker network create eduboost_test_net || true
# remove previous
docker rm -f eduboost_restore_db || true
# run disposable Postgres 17
docker run -d --name eduboost_restore_db --network eduboost_test_net \
  -e POSTGRES_PASSWORD=RestorePass123 -e POSTGRES_DB=postgres postgres:17
# wait
until docker exec eduboost_restore_db pg_isready -U postgres; do sleep 1; done

# run drill in python container on same network, passing envs and --schema=public

docker run --rm --network eduboost_test_net \
  -e DB_ROLLBACK_SOURCE_DATABASE_URL='postgresql://postgres.ezjzbvybbwynqpqnbrdt:Butviewsudden.55555@aws-0-eu-west-1.pooler.supabase.com:6543/postgres' \
  -e DB_ROLLBACK_RESTORE_DATABASE_URL='postgresql://postgres:RestorePass123@eduboost_restore_db:5432/postgres' \
  -e DB_ROLLBACK_PG_RESTORE_ARGS='--schema=public' \
  -v "$PWD":/work -w /work python:3.11-slim bash -lc "\
    set -x; apt-get update -y; apt-get install -y git postgresql-client-17 gcc libpq-dev; \
    pip install --no-cache-dir psycopg2-binary; \
    python scripts/db_backup_restore_rollback_evidence.py --run-drill"
```

- Notes: we install `git` in container to allow `current_commit()` to succeed. Alternatively, pass `DB_ROLLBACK_COMMIT_SHA` to avoid requiring `git`.

8) Outcome and artifacts

- The disposable-run produced a dump and successfully restored `--schema=public` into the disposable Postgres 17 instance.
- Evidence file written: `docs/release/db_backup_restore_rollback_evidence_status.json` with fields updated, for example:
  - `dump_sha256`: `3929277ee796cf2d11e2e15c454dd04522ccdb069c3fd31fc74c625cc3a6d50a`
  - `dump_file_label`: `db_rollback_unknown_20260523192733.dump`
  - `source_table_count`: 26
  - `restore_table_count`: 26
  - `restore_command.return_code`: 0

- Dump file stored in `temp/db_rollback/` inside repo (e.g. `temp/db_rollback/db_rollback_unknown_20260523192733.dump`).

Final working commands (copy/paste)
----------------------------------
1) Apply script patch (already applied in repo):

- Edits made to `scripts/db_backup_restore_rollback_evidence.py` to support `DB_ROLLBACK_PG_RESTORE_ARGS`.

2) Run drill into disposable Postgres container:

```bash
# create network
docker network create eduboost_test_net || true
# remove previous container
docker rm -f eduboost_restore_db || true
# run disposable Postgres 17
docker run -d --name eduboost_restore_db --network eduboost_test_net \
  -e POSTGRES_PASSWORD=RestorePass123 -e POSTGRES_DB=postgres postgres:17
# wait for readiness
until docker exec eduboost_restore_db pg_isready -U postgres; do sleep 1; done
# run drill
docker run --rm --network eduboost_test_net \
  -e DB_ROLLBACK_SOURCE_DATABASE_URL='postgresql://postgres.ezjzbvybbwynqpqnbrdt:Butviewsudden.55555@aws-0-eu-west-1.pooler.supabase.com:6543/postgres' \
  -e DB_ROLLBACK_RESTORE_DATABASE_URL='postgresql://postgres:RestorePass123@eduboost_restore_db:5432/postgres' \
  -e DB_ROLLBACK_PG_RESTORE_ARGS='--schema=public' \
  -v "$PWD":/work -w /work python:3.11-slim bash -lc "set -x; apt-get update -y; apt-get install -y git postgresql-client-17 gcc libpq-dev; pip install --no-cache-dir psycopg2-binary; python scripts/db_backup_restore_rollback_evidence.py --run-drill"
# review evidence
cat docs/release/db_backup_restore_rollback_evidence_status.json
# cleanup
docker rm -f eduboost_restore_db || true
docker network rm eduboost_test_net || true
```

Artifacts produced and locations
-------------------------------
- Evidence JSON: `docs/release/db_backup_restore_rollback_evidence_status.json`
- Evidence MD: `docs/release/db_backup_restore_rollback_evidence_status.md`
- Dump file(s): `temp/db_rollback/*.dump`

Recommendations & notes
-----------------------
- Prefer disposable restore targets for restore verification; do not restore into production or Supabase-managed targets.
- Keep `postgres:17` or `postgresql-client-17` for client/restore tooling to avoid header version incompatibilities.
- Consider adding `--schema=public` by default in the script when the restore target hostname contains `supabase` (detect and warn) to avoid accidental attempts to restore managed schemas. I did not make that automatic change — it's deliberate and up to policy.
- Add an optional `DB_ROLLBACK_COMMIT_SHA` env var so CI/container runs can avoid installing `git`.

Appendix: full terminal logs
---------------------------
The interactive run produced long terminal logs; the key excerpts are captured in the repository's chat-session resources. If you want, I can extract the full logs into `docs/release/drill_logs.txt`.



