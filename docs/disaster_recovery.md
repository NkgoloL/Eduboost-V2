# Disaster recovery plan

## Recovery objectives

| System | RPO | RTO | Notes |
|---|---:|---:|---|
| PostgreSQL transactional database | 24 hours for beta, 1 hour for production | 4 hours for beta, 1 hour for production | Tighten once managed PITR is enabled |
| Redis cache/session store | Best effort | 30 minutes | Refresh-token sessions are disposable; users may need to log in again |
| Object storage/artifacts | 24 hours | 4 hours | Applies to exports, reports, and generated artifacts if externalized |
| LLM providers | No data-loss target | 4 hours | Fail over to alternate provider or disable generation queue |
| Email provider | No data-loss target | 4 hours | Queue transactional emails where possible |
| Payment provider | Provider ledger authoritative | 4 hours | Reconcile using provider event IDs and local idempotency table |

## Backup retention

Recommended production retention:

| Backup class | Retention |
|---|---:|
| Daily encrypted database backups | 35 days |
| Weekly encrypted database backups | 12 weeks |
| Monthly encrypted database backups | 12 months |
| Pre-migration snapshots | At least 35 days |

Backups must be encrypted and stored in a separate failure domain from the primary database.

## Restore validation

Every restore drill must validate:

1. Alembic revision at expected head.
2. Guardian and learner row counts match backup manifest.
3. Consent states and active-consent indexes are queryable.
4. Audit events validate hash/HMAC shape and append-only policy remains in place.
5. Stripe webhook idempotency records are present.
6. A smoke login, learner read, diagnostic read, and POPIA export can complete in the restored environment.

## Monthly restore drill

Run in a clean, isolated environment:

```bash
# 1. Restore latest encrypted backup into disposable database.
# 2. Export DATABASE_URL for the restored database.
DATABASE_URL=postgresql+asyncpg://... alembic upgrade head
PYTHONPATH=. make migration-check
PYTHONPATH=. pytest tests/smoke/ --no-cov
```

Record the drill date, backup ID, restore duration, validation result, and any remediation items in the release evidence bundle.

## Alerting requirements

Backup and restore alerts must cover:

- scheduled backup failure
- backup age exceeding RPO
- backup encryption failure
- restore drill failure
- migration failure
- audit write failure
- database unavailable

## Provider outage plans

| Provider class | Degraded-mode action |
|---|---|
| Cloud hosting | Fail over to last known-good deployment target or maintenance page |
| PostgreSQL | Stop learner writes, keep health/readiness red, preserve incident log |
| Redis | Force session re-login, disable background job status cache if needed |
| LLM provider | Switch provider through LLM gateway or pause generation queue |
| Payment provider | Continue read-only entitlement from cached state; reconcile webhooks later |
| Email provider | Queue notifications and retry with alternate provider |
| Analytics | Drop non-critical analytics events; never block learner flows |
