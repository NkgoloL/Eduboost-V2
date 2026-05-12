# 11. Observability, metrics, logging, tracing, and alerting

## 11.1 Metrics

- [ ] `P0` Verify `/metrics` endpoint works.
- [ ] `P0` Add HTTP request count metric.
- [ ] `P0` Add HTTP latency metric.
- [ ] `P0` Add HTTP error-rate metric.
- [ ] `P0` Add status-code metric.
- [ ] `P0` Add dependency health metric.
- [ ] `P0` Add DB pool metric.
- [ ] `P0` Add Redis operation metric.
- [ ] `P0` Add background job metric.
- [ ] `P0` Add LLM call count metric.
- [ ] `P0` Add LLM latency metric.
- [ ] `P0` Add LLM token usage metric.
- [ ] `P0` Add LLM fallback metric.
- [ ] `P0` Add billing webhook metric.
- [ ] `P0` Add consent lifecycle metric.
- [ ] `P0` Add diagnostic session metric.
- [ ] `P0` Add lesson generation metric.
- [ ] `P0` Add backup success/failure metric.
- [ ] `P0` Add audit write failure metric.
- [ ] `P1` Add active learners metric.
- [ ] `P1` Add lesson completion metric.
- [ ] `P1` Add study-plan adherence metric.
- [ ] `P1` Add parent report open metric.
- [ ] `P1` Add consent conversion metric.
- [ ] `P1` Add churn metric if billing enabled.

## 11.2 Dashboards

- [ ] `P0` Build API dashboard.
- [ ] `P0` Build database dashboard.
- [ ] `P0` Build Redis dashboard.
- [ ] `P0` Build LLM provider dashboard.
- [ ] `P0` Build POPIA operations dashboard.
- [ ] `P0` Build learner journey dashboard.
- [ ] `P0` Build audit dashboard.
- [ ] `P0` Build backup/restore dashboard.
- [ ] `P1` Build billing dashboard.
- [ ] `P1` Build frontend error dashboard.
- [ ] `P1` Build business metrics dashboard.
- [ ] `P2` Build curriculum coverage dashboard.
- [ ] `P2` Build content quality dashboard.

## 11.3 Alerts

- [ ] `P0` Alert when API is down.
- [ ] `P0` Alert on readiness failure.
- [ ] `P0` Alert on high 5xx rate.
- [ ] `P0` Alert on high latency.
- [ ] `P0` Alert when DB unavailable.
- [ ] `P0` Alert when Redis unavailable.
- [ ] `P0` Alert on migration failure.
- [ ] `P0` Alert on audit write failure.
- [ ] `P0` Alert on consent enforcement failure.
- [ ] `P0` Alert on failed backup.
- [ ] `P0` Alert on failed security scan.
- [ ] `P1` Alert on LLM cost spike.
- [ ] `P1` Alert on LLM error spike.
- [ ] `P1` Alert on queue backlog.
- [ ] `P1` Alert on high 4xx rate.
- [ ] `P1` Alert on memory pressure.
- [ ] `P1` Alert on disk pressure.
- [ ] `P1` Alert on abnormal auth failures.
- [ ] `P1` Alert on webhook failure spike.

## 11.4 Logging

- [ ] `P0` Emit structured JSON logs in production.
- [ ] `P0` Include request ID in every backend log.
- [ ] `P0` Include user/actor pseudonymous identifier where safe.
- [ ] `P0` Scrub PII from logs.
- [ ] `P0` Scrub tokens from logs.
- [ ] `P0` Scrub cookies from logs.
- [ ] `P0` Scrub API keys from logs.
- [ ] `P0` Scrub passwords from logs.
- [ ] `P0` Scrub secrets from logs.
- [ ] `P1` Separate audit logs from operational logs.
- [ ] `P1` Add frontend error logging.
- [ ] `P1` Add log retention policy.
- [ ] `P1` Add log access policy.

## 11.5 Tracing

- [ ] `P1` Add OpenTelemetry to frontend.
- [ ] `P1` Add OpenTelemetry to API.
- [ ] `P1` Add OpenTelemetry to service layer.
- [ ] `P1` Add OpenTelemetry to repositories.
- [ ] `P1` Add OpenTelemetry to database calls.
- [ ] `P1` Add OpenTelemetry to Redis calls.
- [ ] `P1` Add OpenTelemetry to LLM provider calls.
- [ ] `P2` Correlate traces with audit events where safe.
- [ ] `P2` Add trace sampling policy.

---

