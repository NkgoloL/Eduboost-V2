# 11. Observability, metrics, logging, tracing, and alerting

## 11.1 Metrics

- [verify] `P0` Verify `/metrics` endpoint works.
- [verify] `P0` Add HTTP request count metric.
- [verify] `P0` Add HTTP latency metric.
- [verify] `P0` Add HTTP error-rate metric.
- [verify] `P0` Add status-code metric.
- [verify] `P0` Add dependency health metric.
- [verify] `P0` Add DB pool metric.
- [verify] `P0` Add Redis operation metric.
- [verify] `P0` Add background job metric.
- [verify] `P0` Add LLM call count metric.
- [verify] `P0` Add LLM latency metric.
- [verify] `P0` Add LLM token usage metric.
- [verify] `P0` Add LLM fallback metric.
- [verify] `P0` Add billing webhook metric.
- [verify] `P0` Add consent lifecycle metric.
- [verify] `P0` Add diagnostic session metric.
- [verify] `P0` Add lesson generation metric.
- [verify] `P0` Add backup success/failure metric.
- [verify] `P0` Add audit write failure metric.
- [verify] `P1` Add active learners metric.
- [verify] `P1` Add lesson completion metric.
- [verify] `P1` Add study-plan adherence metric.
- [verify] `P1` Add parent report open metric.
- [verify] `P1` Add consent conversion metric.
- [verify] `P1` Add churn metric if billing enabled.

## 11.2 Dashboards

- [verify] `P0` Build API dashboard.
- [verify] `P0` Build database dashboard.
- [verify] `P0` Build Redis dashboard.
- [verify] `P0` Build LLM provider dashboard.
- [verify] `P0` Build POPIA operations dashboard.
- [verify] `P0` Build learner journey dashboard.
- [verify] `P0` Build audit dashboard.
- [verify] `P0` Build backup/restore dashboard.
- [verify] `P1` Build billing dashboard.
- [verify] `P1` Build frontend error dashboard.
- [verify] `P1` Build business metrics dashboard.
- [verify] `P2` Build curriculum coverage dashboard.
- [verify] `P2` Build content quality dashboard.

## 11.3 Alerts

- [verify] `P0` Alert when API is down.
- [verify] `P0` Alert on readiness failure.
- [verify] `P0` Alert on high 5xx rate.
- [verify] `P0` Alert on high latency.
- [verify] `P0` Alert when DB unavailable.
- [verify] `P0` Alert when Redis unavailable.
- [verify] `P0` Alert on migration failure.
- [verify] `P0` Alert on audit write failure.
- [verify] `P0` Alert on consent enforcement failure.
- [verify] `P0` Alert on failed backup.
- [verify] `P0` Alert on failed security scan.
- [verify] `P1` Alert on LLM cost spike.
- [verify] `P1` Alert on LLM error spike.
- [verify] `P1` Alert on queue backlog.
- [verify] `P1` Alert on high 4xx rate.
- [verify] `P1` Alert on memory pressure.
- [verify] `P1` Alert on disk pressure.
- [verify] `P1` Alert on abnormal auth failures.
- [verify] `P1` Alert on webhook failure spike.

## 11.4 Logging

- [verify] `P0` Emit structured JSON logs in production.
- [verify] `P0` Include request ID in every backend log.
- [verify] `P0` Include user/actor pseudonymous identifier where safe.
- [verify] `P0` Scrub PII from logs.
- [verify] `P0` Scrub tokens from logs.
- [verify] `P0` Scrub cookies from logs.
- [verify] `P0` Scrub API keys from logs.
- [verify] `P0` Scrub passwords from logs.
- [verify] `P0` Scrub secrets from logs.
- [verify] `P1` Separate audit logs from operational logs.
- [verify] `P1` Add frontend error logging.
- [verify] `P1` Add log retention policy.
- [verify] `P1` Add log access policy.

## 11.5 Tracing

- [verify] `P1` Add OpenTelemetry to frontend.
- [verify] `P1` Add OpenTelemetry to API.
- [verify] `P1` Add OpenTelemetry to service layer.
- [verify] `P1` Add OpenTelemetry to repositories.
- [verify] `P1` Add OpenTelemetry to database calls.
- [verify] `P1` Add OpenTelemetry to Redis calls.
- [verify] `P1` Add OpenTelemetry to LLM provider calls.
- [verify] `P2` Correlate traces with audit events where safe.
- [verify] `P2` Add trace sampling policy.

---



## 11.6 Repository-side implementation evidence

- [verify] Observability stack decision is documented in `docs/adr/ADR-011-observability-stack.md`.
- [verify] Observability architecture is documented in `docs/observability/production_observability_architecture_contract.md`.
- [verify] Metrics and SLO evidence is documented in `docs/observability/metrics_slo_contract.md`.
- [verify] Logging and tracing evidence is documented in `docs/observability/logging_tracing_contract.md`.
- [verify] Alerting and incident routing evidence is documented in `docs/observability/alerting_incident_routing_contract.md`.
- [verify] Dashboard and runbook evidence is documented in `docs/observability/dashboard_runbook_contract.md`.
- [verify] Telemetry privacy and retention evidence is documented in `docs/observability/telemetry_privacy_retention_contract.md`.
- [verify] Required runbooks are present under `docs/observability/runbooks/`.
- [verify] Deterministic repository contracts live in `app/modules/observability/production_readiness_contracts.py`.
- [verify] Repository validation is provided by `scripts/check_observability_production_readiness.py`.
- [verify] Domain validation wrapper is provided by `scripts/check_domain_11_observability_evidence.py`.
- [verify] Unit coverage is provided by `tests/unit/test_observability_production_readiness.py`.
- [verify] Make target is `make observability-production-readiness-check`.

### Verification boundary

This implementation provides repository-side observability, metrics, logging, tracing, alerting, dashboard, runbook, telemetry privacy, and retention readiness evidence. It does not configure a live telemetry backend, emit production telemetry, create dashboards, send alerts, or authorize production launch.
