# Observability Runbook

EduBoost V2 exposes operational telemetry through structured logs, Prometheus metrics, Alertmanager alerts, and Grafana dashboards. These controls must be live before processing real learner data.

## Signals

| Signal | Source | Purpose |
|---|---|---|
| Structured logs | API stdout / log collector | Request, error, and operational event diagnosis |
| Request ID | `X-Request-ID` header and log context | Cross-service correlation |
| Metrics | `/metrics` | Runtime health, latency, errors, LLM usage, consent events, DB/Redis state |
| Readiness | `/ready` | Dependency-aware promotion gate |
| Alerts | `prometheus/alerts.yml` | Page/warn on SLO or compliance-relevant failures |
| Dashboards | `grafana/dashboards/` | Operator triage and product-health review |

## Critical metrics

- `eduboost_http_requests_total`
- `eduboost_http_request_duration_seconds`
- `eduboost_readiness_component_status`
- `eduboost_db_pool_size_total`
- `eduboost_db_pool_checkedout_total`
- `eduboost_db_pool_overflow_total`
- `eduboost_redis_connected_clients`
- `eduboost_arq_jobs_total`
- `eduboost_llm_requests_total`
- `eduboost_llm_tokens_total`
- `eduboost_consent_events_total`
- `eduboost_consent_gate_blocks_total`
- `eduboost_audit_write_failures_total`
- `eduboost_backup_last_success_timestamp`
- `eduboost_backup_failures_total`

## Alert response

### API down

1. Check deployment rollout and container restarts.
2. Query `/health` and `/ready` from inside the cluster/network.
3. Inspect recent application logs by `request_id` and `app_version`.
4. Roll back to the previous known-good image if the failure follows a deploy.

### Readiness failure

1. Read `/ready` and identify the failed critical component.
2. For PostgreSQL, inspect managed DB health, connection limits, and migrations.
3. For Redis, inspect service health, memory pressure, and connectivity.
4. Keep production promotion blocked until readiness is stable.

### Audit write failure

1. Treat as compliance-critical.
2. Stop non-essential learner-data processing if writes cannot be restored quickly.
3. Preserve application logs and database diagnostics for postmortem.
4. Do not backfill audit events unless the reconstructed source and timestamps are explicitly documented.

### Backup failure

1. Check the backup job log and object-storage destination.
2. Manually run a backup into the configured backup bucket if automated retries fail.
3. Verify encryption, checksum, and restore-readability.
4. Attach evidence to the release/operations record.

## PII/logging rules

Operational logs must not contain passwords, JWTs, refresh tokens, cookies, API keys, SA ID numbers, emails, phone numbers, or learner free-text content. Audit logs are separate from operational logs and have different retention semantics.
