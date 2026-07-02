---
title: "RR-008 Grafana Alert Linkage"
status: authority
owner: operations
---

# RR-008 Grafana Alert Linkage

Grafana alert linkage recorded: true

## Dashboard coverage

Operational readiness requires dashboards or equivalent metric views for:

- API readiness and deep health;
- learner diagnostic latency;
- lesson generation latency and error rate;
- parent portal latency and error rate;
- Postgres health;
- Redis health;
- AI gateway/LLM request volume and failures;
- consent/export/erasure flow errors.

## Alert routing

Alert routing must link to incident response runbooks and identify the handoff owner for security, privacy, data, and service-availability incidents.

## Existing references

- `grafana/` dashboard assets;
- `prometheus/` monitoring assets;
- `docs/operations/observability.md`;
- `docs/observability/metrics_slo_contract.md`;
- `docs/observability/alerting_incident_routing_contract.md`.

## Boundary

This file records linkage. RR-016 remains responsible for monitoring dashboard drill verification.
