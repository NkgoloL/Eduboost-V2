---
title: "ADR-027 — Observability Endpoint Access Control"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-027 — Observability Endpoint Access Control

**Status:** Accepted  
**Date:** 2026-06-12  
**Decision owner:** Platform / Engineering  
**Phase:** 7 (Deployment and Security Hardening)

---

## Context

Two operational endpoints in `app/api_v2.py` lacked access control:

1. **`/metrics`** — Prometheus scrape endpoint that exposes internal counters,
   latency histograms, and business metrics. Leaking this to the public
   internet discloses implementation details useful for attackers.

2. **`/__dev/slow_query`** — Developer diagnostic that executes `pg_sleep()`
   to trigger slow-query logging. Should never be reachable in production.

---

## Decision

### `/metrics`

**Chosen approach:** Defence-in-depth — infra-layer blocking + app-level IP check.

- **Primary control:** The Nginx/ACA ingress does NOT expose `/metrics` to the
  public internet. For ACA, the Prometheus scrape path is reachable only from
  the managed environment's internal network.
- **Fallback control:** The FastAPI handler rejects requests whose source IP is
  not a loopback address (`127.x`, `::1`) or an RFC-1918 private range when
  `APP_ENV == production`.

**Why not a bearer token?**
Prometheus scrapers are typically configured at the infra level without bearer
tokens. Adding a token creates operational friction without a meaningful
security gain given the infra-layer primary control.

### `/__dev/slow_query`

Already gated with `if settings.is_production(): return 404` before Phase 7.
No additional change required. Documented here for completeness.

---

## Consequences

### Positive
- No metrics data is exposed to unauthenticated public traffic in production.
- Infra-layer blocking is zero-overhead (no Python code executed for blocked requests).
- App-level IP check provides a defence-in-depth backstop if ingress is misconfigured.

### Negative
- IP-based access control can fail if the scraper IP changes (e.g., ACA revision rollout).
  Mitigation: monitor Prometheus scrape failures in Grafana alerts.

---

## References

- Phase 7 execution plan: `docs/roadmap/execution/phase_7_execution_plan.md` §7.7
- Implementation: `app/api_v2.py` `/metrics` handler
