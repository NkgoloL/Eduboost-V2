---
title: "ADR-031 — Durable AI Operations and Budget Authority"
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
# ADR-031 — Durable AI Operations and Budget Authority

**Status:** Accepted for Phase 6 implementation  
**Date:** 2026-06-15

## Context

Earlier token limits used Redis or in-process counters. Those counters are useful for fast throttling but are not sufficient as an auditable, multi-worker source of truth. They can expire, be flushed, diverge between processes, or fail without leaving durable cost evidence.

## Decision

PostgreSQL is the authoritative ledger for AI token reservations, completed usage, and estimated cost. Redis remains an optional fast pre-check, not the financial or governance authority.

Every governed provider call must use a stable operation id, reserve an upper-bound token amount before the call, and either finalize or release the reservation. Pending reservations expire through a durable ARQ maintenance job. Usage events are append-only.

Deterministic or mock providers are prohibited in production. Administrative usage and provider-health endpoints are role protected and never expose prompts or completions.

## Consequences

- Concurrent calls cannot overspend the same user or tenant budget without locking the same counters.
- Usage and cost evidence survives Redis loss and process restarts.
- Provider telemetry can be reconciled to operation ids.
- A PostgreSQL failure fails closed for governed AI calls.
- Existing Redis counters may temporarily remain as defence-in-depth while callers migrate to the durable authority.
