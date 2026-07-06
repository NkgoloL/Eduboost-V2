---
title: RR-008 Grafana Alert Linkage
status: authority
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
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
