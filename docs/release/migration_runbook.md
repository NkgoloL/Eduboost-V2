# Database Migration Evidence Runbook

This runbook defines how to produce database migration evidence for release readiness.

## Preconditions

- Use a disposable PostgreSQL database such as `eduboost_test`.
- Do not run destructive migration evidence capture against production or shared dev databases.
- Confirm `DATABASE_URL` points to the disposable database.
- Confirm the branch and commit SHA are recorded.

## Commands

Capture migration evidence:

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/eduboost_test"
make migration-evidence-capture
```

Capture with a one-step downgrade/upgrade drill:

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/eduboost_test"
PYTHONPATH=. python3 scripts/capture_migration_evidence.py --include-downgrade
```

Validate latest captured evidence shape:

```bash
make migration-evidence-schema-check
```

Validate latest captured evidence passed:

```bash
make migration-evidence-check
```

## Outputs

| File | Purpose |
|---|---|
| `docs/release/migration_latest.json` | Machine-readable migration command evidence |
| `docs/release/migration_latest.md` | Human-readable latest migration run |
| `docs/release/migration_evidence.md` | Stable release gate template |

## Acceptance rule

`migration_evidence.md` should remain pending until a release owner accepts a real disposable PostgreSQL migration run.


## Credential policy

Do not use placeholder credentials such as:

```text
postgresql+asyncpg://user:pass@localhost:5432/eduboost_test
```

The database name can be disposable, but the credential must be real for that disposable database.

For local tooling-debug only, the script supports:

```bash
PYTHONPATH=. python3 scripts/capture_migration_evidence.py --allow-placeholder-credentials
```

Do not use that flag for release evidence.
