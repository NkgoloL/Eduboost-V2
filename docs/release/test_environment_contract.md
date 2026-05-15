# Test Environment Contract

EduBoost tests must run against explicit local/test configuration. Integration tests must not silently mutate production-like databases.

## Required local/test environment properties

| Variable | Requirement |
|---|---|
| `APP_ENV` or `ENVIRONMENT` | Must not be `production` or `prod` for local tests. |
| `DATABASE_URL` | Must point to SQLite or a clearly disposable database such as `eduboost_test` or a name containing `test`. |
| `ENCRYPTION_KEY` | Must be valid base64 for 32 bytes, which is normally 44 characters including padding. |
| `ALLOWED_ORIGINS` | Must parse as JSON list or comma-separated URL list. |
| `JWT_SECRET` / `JWT_SECRET_KEY` | Must not be an obvious placeholder in shared/dev environments. |

## Commands

```bash
make test-env-check
make reset-test-db
```

`reset-test-db` must refuse to run unless the database name is clearly test/disposable, or unless a developer explicitly sets an override after verifying the target.
