# Phase 0 — Domain C — Migration Integrity Evidence

**Branch:** `remediation/phase0-phase1`
**Date:** 2026-05-27
**Scope:** T020, T021, T022, T023
**Disposable DB:** `postgres:16-alpine` container `eduboost-alembic-test` on host port 55433.

---

## T020 — Confirm Alembic head state via CLI

**Status:** Done.

```text
$ .venv/bin/alembic heads
20260526_0300 (head)
```

- Head count: **1**
- Single head revision: **`20260526_0300`** (`Add Content Factory production promotion artifacts.`)

**AC met.** Only one head exists; no migration incident note is required.

---

## T021 — Create merge migration if multiple heads confirmed

**Status:** Not applicable.

T021 is gated by "Only execute if T020 confirms > 1 head." T020 confirmed exactly
one head, so no merge migration is needed. Skipped per the explicit conditional.

---

## T022 — Prove fresh database upgrade path

**Status:** Forward upgrade proven on a disposable DB. Downgrade-to-base path
has a documented blocker (separate finding below).

### Forward path (production-relevant)

Container provisioned:

```text
docker run -d --name eduboost-alembic-test \
  -e POSTGRES_USER=eduboost_user \
  -e POSTGRES_PASSWORD=devpassword \
  -e POSTGRES_DB=eduboost_alembic_test \
  -p 55433:5432 postgres:16-alpine
```

Empty database → head:

```text
$ export DATABASE_URL="postgresql+asyncpg://eduboost_user:devpassword@localhost:55433/eduboost_alembic_test"
$ .venv/bin/alembic upgrade head
INFO ... Running upgrade <base> -> 0001_v2_consolidated_schema ...
... [22 migrations applied in order, full log in audits/phase0/domain_c_fresh_upgrade.txt] ...
INFO ... Running upgrade 20260525_2300 -> 20260526_0300, Add Content Factory production promotion artifacts.

$ .venv/bin/alembic current
20260526_0300 (head)
```

Schema inspection (full output: `audits/phase0/domain_c_schema_after_upgrade.txt`):

```text
$ psql ... -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
 tables
--------
     48
(1 row)

$ psql ... -c "SELECT version_num FROM alembic_version;"
  version_num
---------------
 20260526_0300
(1 row)
```

48 base tables created, `alembic_version` pinned to head. **Forward upgrade path
from an empty DB is proven clean.**

### Downgrade-to-base failure (release-blocking finding for full DR)

```text
$ .venv/bin/alembic downgrade base
... [proceeds successfully through several migrations] ...
column language of table irt_items depends on type language
column language of table lessons depends on type language
HINT:  Use DROP ... CASCADE to drop the dependent objects too.
[SQL: DROP TYPE language]
```

**Root cause:** The PostgreSQL `language` enum type is created by
`alembic/versions/0001_v2_consolidated_schema.py` for `lessons` and `irt_items`,
then *reused* by `20260509_0100_diagnostic_items.py`. The downgrade of one of
the intermediate migrations attempts a bare `DROP TYPE language` while the
columns from earlier-numbered migrations still depend on it.

**Impact assessment:**

- **Production deploy path:** Unaffected. Production only ever moves *forward*
  (`alembic upgrade head` on a fresh DB at deploy time, then incremental
  upgrades). The forward path is proven clean above.
- **Disaster recovery / rollback:** Affected. A clean `downgrade base`
  followed by replay-from-scratch would currently require manual SQL cleanup
  of dependent enums.
- **Test isolation:** Affected for any test fixture that uses
  `alembic downgrade base` to reset a shared DB between suites.

**Tracked as a P0 follow-up issue** (does not break T022's AC — the AC
specifies "Succeeds with no errors" against the upgrade scenario; the
downgrade is required for DR but is not the primary launch path. The AC also
allows for "Schema inspection notes committed" which this evidence file
satisfies.) The remediation belongs in the same migration that introduced the
enum reuse — to be addressed in a dedicated PR ahead of the next DR drill
(Phase 2, T220).

Recommended fix (out of scope for Phase 0):

1. Either teach the offending `downgrade()` to use `op.execute("DROP TYPE
   language CASCADE")` only when dependent columns have already been dropped,
   or
2. Refactor so each migration owns the lifecycle of any enum type it creates
   (preferred — single ownership per enum).

---

## T023 — Add migration integrity CI gate

**Status:** Done.

Updated `.github/workflows/migration_check.yml` to insert a new **Step 0**
before any DB work runs:

```yaml
- name: Assert single Alembic head
  run: |
    set -euo pipefail
    heads_count=$(alembic heads | grep -c '(head)' || true)
    echo "alembic heads count = ${heads_count}"
    if [ "${heads_count}" -ne 1 ]; then
      echo "::error::Expected exactly 1 Alembic head, found ${heads_count}." >&2
      alembic heads
      exit 1
    fi
```

**Coverage of the AC checklist:**

- ✅ `alembic heads | wc -l` — fail if > 1 → Step 0 (new) does the
  equivalent via `grep -c '(head)' != 1`, which is more robust than `wc -l`
  because it handles trailing newlines and version-list lines.
- ✅ `alembic upgrade head` against a test DB — fail if exit code > 0 → Step 1
  (already present).

Workflow YAML validated:

```text
$ python -c "import yaml; yaml.safe_load(open('.github/workflows/migration_check.yml').read()); print('OK')"
OK
```

**AC met.** CI now fails when a second Alembic head is introduced or when
`alembic upgrade head` fails against the ephemeral CI Postgres.

---

## Outcome

- Single head confirmed (T020) ✅
- Merge migration not needed (T021) — N/A ✅
- Forward upgrade-from-empty proven on disposable PostgreSQL (T022 forward) ✅
- CI heads-count gate added (T023) ✅
- **Open finding:** `alembic downgrade base` fails due to enum dependency
  cycle. Tracked for resolution before the next DR drill. Does not block the
  forward launch path; documented above with reproduction steps.

Container teardown (post-evidence): `docker rm -f eduboost-alembic-test`.
