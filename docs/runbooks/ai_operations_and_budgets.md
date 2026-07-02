---
title: "AI Operations and Budget Runbook"
status: active-runbook
owner: operations
reviewers: [operations, engineering, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [docs/runbooks, docs/operations]
---

# AI Operations and Budget Runbook

## Purpose

Operate the Phase 6 durable AI usage ledger, reservations, budgets, provider health, and production provider guards.

## Key endpoints

- `GET /api/v2/admin/ai-operations/budgets/users/{user_id}`
- `GET /api/v2/admin/ai-operations/budgets/tenants/{tenant_id}`
- `GET /api/v2/admin/ai-operations/usage`
- `GET /api/v2/admin/ai-operations/providers/health`
- `GET /api/v2/admin/ai-operations/reservations`
- `POST /api/v2/admin/ai-operations/reservations/{operation_id}/cancel`

## Alerts

Investigate when:

- tenant usage reaches 80% of the monthly token limit;
- a budget block rate spikes;
- pending reservations exceed their TTL;
- provider error rate is 10% or higher over 24 hours;
- provider error rate reaches 50%;
- append-only trigger failures appear;
- deterministic or mock provider configuration is detected outside test.

## Stale reservation recovery

The ARQ job `expire_ai_usage_reservations` runs every five minutes. To execute manually:

```bash
.venv/bin/arq app.modules.jobs.WorkerSettings
# or enqueue expire_ai_usage_reservations through the normal durable job helper
```

Never edit `ai_usage_events`. They are append-only evidence. Correct a reporting issue by appending a reconciliation record in a separately approved change.

## Budget incident

1. Confirm current durable counter and reservation totals.
2. Check whether a provider call completed without finalization.
3. Allow the expiry job to release stale reservations or cancel a known failed operation through the admin endpoint.
4. Do not raise limits during an incident without owner approval and a recorded reason.
5. Preserve raw operation ids, timestamps, provider/model metadata, and relevant metrics.

## Redis loss

The durable PostgreSQL ledger remains authoritative. Redis counters may be rebuilt or flushed, but governed AI calls must continue to reserve against PostgreSQL. If PostgreSQL accounting is unavailable, AI calls fail closed or return a non-deceptive safe fallback.
