---
title: "ADR-023 — Frontend Upgrade (React 19 + Next 15)"
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
# ADR-023 — Frontend Upgrade (React 19 + Next 15)

```text
Status: Accepted
Date: 2026-05-28
Owner: Frontend Tech Lead
RC Gate: RC1 (extends into RC2)
Blocks: FE-PR-001 · FE-PR-002 · FE-PR-003 · FE-P1-021 · FE-NS-004
Reviewers: Backend Lead, POPIA Compliance Officer
Evidence: FE-SPIKE-001/002/003 reports, FE-PR-002 verification log
```

## Context

Frontend spikes FE-SPIKE-001 through FE-SPIKE-003 evaluated the risk of upgrading to React 19 + Next 15, confirmed bundle feasibility, and determined that Partial Prerendering (PPR) must remain disabled until Next.js ships stable support. RC1 work depends on locking the upgrade path plus the associated rollback discipline captured in FE-PR-001 and FE-PR-002.

### Spike Results Summary

- **FE-SPIKE-001** — React 19 + Next 15 compatibility ✅ proceed; Docker builds succeed.
- **FE-SPIKE-002** — Bundle feasibility ✅ acceptable under 120 kB with ongoing monitoring.
- **FE-SPIKE-003** — PPR + deployment viability ✅ complete / **DEFER**; keep PPR disabled.

## Decision

- Adopt React 19 and Next 15 immediately for RC1/RC2 implementation.
- Keep PPR disabled across all authenticated routes until Next.js exposes GA support and a follow-up spike succeeds.
- Treat all other major dependency upgrades as deferred unless tied to explicit RC gates or spike outcomes.

### Required Safeguards

1. Resolve multi-lockfile warnings via `outputFileTracingRoot` and pnpm discipline.
2. Prevent or clean root-owned `.next` artifacts (cleanup script + Makefile target).
3. Codify Docker/runtime build discipline (multi-stage `runner`, `pnpm install --frozen-lockfile`).
4. Maintain bundle-size monitoring (`pnpm run analyze`, gzip checks) after every dependency-heavy PR.
5. Enforce environment validation + synthetic error monitoring to catch regressions early.

## Consequences

### Positive

- Unlocks modern React features and Next 15 performance improvements.
- Aligns the stack with current ecosystem baselines, simplifying future upgrades.
- Spike-backed plan reduces unknown risk and provides evidence for compliance auditors.

### Negative

- Requires strict Docker hygiene to avoid root-owned artifacts.
- Demands continuous bundle + lockfile monitoring to prevent regressions.
- PPR benefits remain unavailable until a future retry.

## Implementation Requirements

- **FE-PR-001** — ADR governance, rollback plan, backlog metadata (**done**).
- **FE-PR-002** — Docker/runtime hardening, pnpm discipline, env validation, monitoring, `.next` cleanup, bundle guardrails (**done**).
- **FE-PR-003** — Strict TypeScript/lint to catch regressions introduced by the upgrade (**next**).

## Rollback Strategy

- Maintain version-pinned Docker images for the pre-upgrade state.
- Keep Supabase fallback documented (`ADR-001-rollback`) so auth surfaces can revert quickly if FastAPI/JWT issues arise post-upgrade.
- Monitor bundle baselines; if gzipped shared chunks exceed agreed thresholds, revert the offending PR.
- Trigger environment-specific rollback when health checks, env validation, or monitoring alerts fail.

## Related Decisions

- ADR-001 — Frontend Auth Model (FastAPI JWT + httpOnly cookies).
- ADR-006 — RSC boundaries (PPR disabled).
- ADR-012 — CI/CD Infrastructure Deployment (deployment discipline).

## Implementation Tracking

| Item | Status |
| --- | --- |
| FE-PR-001 — ADRs, rollback plan, backlog metadata | ✅ Completed |
| FE-PR-002 — Docker/runtime, pnpm discipline, env validation, monitoring, `.next` cleanup, bundle guardrails | ✅ Completed |
| FE-PR-003 — TypeScript strictness, lint | ⏳ Pending |
| FE-P1-021 — Bundle analyzer report | ✅ Captured via FE-SPIKE-002 |
| FE-NS-004 — Bundle target enforcement | ⏳ Pending (depends on FE-PR-006+) |
