---
title: "ADR-004 — AI Tutor Proxy & Safety Envelope"
status: active
owner: frontend
reviewers: [frontend, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-004 — AI Tutor Proxy & Safety Envelope

```text
Status: Draft (RC5 gate)
Date: 2026-05-28
Owner: Frontend Tech Lead
RC Gate: RC5
Blocks: FE-P2-086..096 · FE-PR-013
Reviewers: POPIA Compliance Officer, Information Officer, Safety Lead
Evidence: FE-SPIKE-005 (to be completed), backend tutor proxy design, Safety Board checklist
```

## Context

RC5 introduces an AI tutor experience with streaming responses, voice input, and guardian review. The tutor must never connect directly to Anthropic/Claude from the browser, and every utterance must be audited. Until the spike proves feasibility, we record the intended architecture.

## Decision

- Tutor interactions flow through a server-side proxy route (`src/app/api/tutor/session/route.ts`) hosted in Next.js, which in turn calls the FastAPI tutor orchestrator. The browser never contacts Anthropic directly.
- Streaming uses SSE/WebSockets from the proxy to the client; messages are scrubbed and logged before delivery.
- Rate limits enforced server-side (per learner, per guardian) backed by Redis.
- Guardian review UI relies on the same audit log entries; no separate storage of tutor transcripts in the client.

## Consequences

### Positive

- Keeps API keys server-side and enforces consistent safety filters.
- Enables unified audit replay for tutor conversations.

### Negative

- Increases latency versus direct browser calls.
- Requires dual infrastructure changes (Next.js route + FastAPI orchestrator).

## Implementation Notes

1. Complete FE-SPIKE-005 before implementing FE-PR-013.
2. Document content filters and prompt templates in `docs/frontend/tutor_safety_contract.md` (future work).
3. Add integration tests that simulate streaming responses with synthetic data only.

## Compliance & Evidence

- Safety Board and POPIA approvals required before moving status from Draft to Accepted.
