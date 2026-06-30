# Deployment Runbook

## Authorised target

The authorised V2 deployment target is Azure Container Apps unless a new ADR supersedes that decision. Kubernetes manifests are retained as archived/reference assets and must stay compatible with the canonical runtime.

## Runtime contract

| Item | Value |
|---|---|
| API entrypoint | `app.api_v2:app` |
| Liveness | `/health` |
| Readiness | `/ready` |
| Metrics | `/metrics` |
| OpenAPI | `/openapi.json` |
| Docs | `/docs` |

## Pre-deploy gates

Run the following before staging or production promotion:

```bash
make openapi-check
make migration-check
make ops-check
APP_ENV=staging ENV_FILE=.env.staging make env-check
make release-evidence
```

For a live staging environment:

```bash
STAGING_URL=https://staging.example.com make staging-smoke
```

## Rollout steps

1. Build the backend image from `docker/Dockerfile.v2`.
2. Attach OCI labels for commit SHA, version, build date, and source repository.
3. Push image to the authorised registry.
4. Run Alembic migrations against staging.
5. Deploy staging.
6. Run staging smoke checks.
7. Confirm alerts/dashboards receive data.
8. Promote to production only after the release checklist and evidence manifest are complete.

## Rollback

1. Stop traffic shift or pause rollout.
2. Restore the previous known-good image.
3. Confirm `/health`, `/ready`, and `/metrics`.
4. Do not roll back data migrations unless the migration rollback plan explicitly permits it.
5. Open an incident record if learner data, consent enforcement, or audit logging was affected.
