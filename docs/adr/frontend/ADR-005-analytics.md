---
title: "ADR-005 — Analytics & Consent Tiers (Plausible Self-Host)"
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
# ADR-005 — Analytics & Consent Tiers (Plausible Self-Host)

```text
Status: Draft (RC4 gate)
Date: 2026-05-28
Owner: Frontend Tech Lead + POPIA Compliance Officer
RC Gate: RC4
Blocks: FE-P4-044..049
Reviewers: POPIA Compliance Officer, Information Officer
Evidence: POPIA analytics requirements, Plausible deployment runbook (backend), FE-SPIKE-002 bundle report
```

## Context

Analytics for RC4 must respect POPIA consent tiers and avoid third-party trackers such as Google Analytics or Meta Pixel. We plan to self-host Plausible, emitting only aggregated, non-identifiable events with explicit guardian opt-in. Until consent tooling matures, analytics remains disabled.

## Decision

- Use self-hosted Plausible running within EduBoost’s infrastructure; no external third-party trackers.
- Analytics bundle loads only after guardian opt-in. Deferred dependency register (FE-P1-019) records `plausible-tracker` as RC4-only.
- Events mirror the audit log to avoid divergent schemas, but exclude learner identifiers (replace with hashed pseudonyms stored server-side).
- Lighthouse/perf regressions must be measured because analytics scripts run in RC4 offline contexts.

## Consequences

### Positive

- Maintains POPIA compliance and avoids leaking data to external vendors.
- Simplifies consent handling because Plausible can be toggled via server-rendered script tags per guardian.

### Negative

- Requires self-hosted Infra + maintenance.
- Delays analytics instrumentation until RC4, so early product insights rely on audit logs instead.

## Implementation Notes

1. Complete guardian consent UI (RC3) before exposing analytics toggles.
2. Add CI guard to fail if Plausible bundle exceeds 5 kB gzipped after minification.
3. Ensure `NEXT_PUBLIC_ENABLE_ANALYTICS` default is `false`; only set to `true` in RC4+ deployments with Compliance approval.

## Compliance & Evidence

- POPIA Compliance Officer sign-off recorded in `docs/adr/frontend/sign-off.md` when status changes to Accepted.
