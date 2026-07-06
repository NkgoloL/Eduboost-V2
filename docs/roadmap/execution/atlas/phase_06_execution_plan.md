---
title: Phase 6 Execution Plan — Durable AI Operations, Budget Authority, and Production Hardening
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Phase 6 Execution Plan — Durable AI Operations, Budget Authority, and Production Hardening

**Document version:** 1.0  
**Date:** 2026-06-15  
**Status:** Draft — approval required before execution  
**Phase:** 06  
**Branch:** `feature/atlas-phase-06-ai-operations-and-production-hardening`  
**Base branch:** `master`  
**Base commit:** TBD at start gate  
**Phase owner:** TBD  
**Engineering approver:** TBD  
**Operations owner:** TBD  
**Security/privacy reviewer:** TBD  
**Evidence custodian:** TBD  
**Independent auditor:** TBD  
**Canonical plan path:** `docs/roadmap/execution/atlas/phase_06_execution_plan.md`  
**Evidence path:** `docs/release-evidence/atlas/phase-06/`

`PHASE_06_START_APPROVED=true`

> No approved and committed execution plan, no Phase 6 implementation. No complete implementation report, evidence pack, independent audit, canonical merge, and post-merge verification, no Phase 6 completion.

---

## 1. Objective

Make PostgreSQL the durable authority for AI token reservations, actual usage, estimated cost, and budget enforcement across governed AI operations, while preserving Redis as an optional fast guard only.

Phase 6 also hardens production provider selection, exposes privacy-safe operations telemetry, schedules reservation recovery, and prevents deterministic/mock inference in production.

## 2. Measurable outcomes

Phase 6 succeeds only when:

1. Every integrated governed provider call has a stable operation id.
2. Token capacity is reserved before the provider call.
3. Concurrent calls cannot overspend user-daily or tenant-monthly limits.
4. Actual usage is finalized exactly once.
5. Failed or abandoned reservations are released or expire automatically.
6. Usage events are append-only and survive Redis/process loss.
7. Admin endpoints expose budget, usage, reservation, and provider-health information without prompt or completion content.
8. Deterministic/mock providers fail closed outside the test environment.
9. Phase 1–5 fast and PostgreSQL regressions remain green.
10. The full Atlas plan/report/evidence/audit set is complete.

## 3. Preconditions

- [ ] Phase 5 is `Verified Complete` in `docs/roadmap/PHASE_STATUS_REGISTER.md`.
- [ ] Phase 5 plan, implementation report, evidence index, audit report, and raw evidence exist under Atlas paths.
- [ ] Clean canonical checkout and base SHA are recorded.
- [ ] Current migration head is `20260615_1200_p5_tutor`.
- [ ] Phase 1–5 fast verifiers pass.
- [ ] PostgreSQL/pgvector Docker verification is available.
- [ ] Python from `.venv/bin/python` or `PYTHON_BIN` is Python 3.11 or newer.
- [ ] User-daily and tenant-monthly token limits are approved.
- [ ] Pricing assumptions and non-billing nature of estimated cost are documented.
- [ ] Auditor scope is accepted.

## 4. In scope

- Durable AI usage reservations.
- User-daily and tenant-monthly token counters.
- Append-only completed usage events.
- Estimated provider/model cost telemetry.
- Idempotent reserve/finalize/cancel flows.
- Row locking and concurrent overspend prevention.
- Reservation expiry and ARQ maintenance job.
- Tutor integration with the durable budget authority.
- Admin budget, usage, reservation, and provider-health APIs.
- Production prohibition of deterministic/mock providers.
- Prometheus metrics and operations runbook.
- Alembic migration, PostgreSQL tests, regressions, evidence, and audit.

## 5. Out of scope

- Customer invoicing or financial accounting.
- Automatic purchase of provider quota.
- Dynamic price discovery from providers.
- Full FinOps forecasting.
- Billing-plan changes.
- Phase 7 curriculum expansion.
- Phase 8 technical-debt remediation.

## 6. Architecture decision

PostgreSQL is the source of truth. The core flow is:

```text
request
  → fast Redis guard (optional defence-in-depth)
  → PostgreSQL reserve with locked user/tenant counters
  → provider call
  → PostgreSQL finalize exactly once
  → append-only usage event
  → metrics and operations views
```

Pending reservations expire after a bounded TTL and are released by ARQ. If durable accounting is unavailable, governed AI calls fail closed or return an honest safe fallback.

## 7. Data model

### `ai_budget_counters`

Composite key: `scope_type`, `scope_id`, `period_key`.

Stores:

- used tokens;
- reserved tokens;
- estimated used cost;
- update time.

### `ai_usage_reservations`

Stores:

- stable unique operation id;
- user, tenant, and purpose;
- estimated tokens;
- pending/finalized/cancelled/expired state;
- expiry and finalization timestamps;
- privacy-safe metadata.

### `ai_usage_events`

Append-only record of:

- operation/reservation identity;
- provider and model;
- prompt, completion, and total tokens;
- estimated cost;
- success/fallback/blocked/error outcome;
- timestamp and privacy-safe metadata.

## 8. Security and privacy rules

- Actor identity comes from authenticated context, never request payloads.
- Admin endpoints require the canonical admin dependency.
- No prompts, completions, learner questions, or tutor answers are stored in the usage ledger.
- Usage metadata may contain only approved non-sensitive dimensions.
- Append-only events cannot be updated or deleted through normal database access.
- Unknown API fields are rejected.
- Production deterministic/mock provider selection raises at startup or construction.
- Operation ids must not contain raw personal information.

## 9. Work breakdown

| ID | Work item | Acceptance criterion |
|---|---|---|
| P6-001 | Approve plan and record baseline | Plan committed before code; Phase 5 boundary verified |
| P6-010 | Add AI operations models and migration | Empty DB and Phase 5-head upgrades pass |
| P6-011 | Add append-only trigger and constraints | Update/delete attempts fail |
| P6-020 | Implement reserve/finalize/cancel service | Idempotency and row locking proven |
| P6-021 | Implement budget limits and cost estimation | Approved limits and pricing tests pass |
| P6-022 | Integrate learner tutor | Durable reserve/finalize path used for provider success |
| P6-023 | Add stale reservation expiry | ARQ job registered and scheduled; never invents usage |
| P6-030 | Add protected admin API | Budget, usage, reservation, and provider health available |
| P6-031 | Add metrics and runbook | Metrics registered; response actions documented |
| P6-032 | Add production provider guards | Deterministic/mock modes rejected outside test |
| P6-040 | Add unit/registration tests | Zero failures, unexpected skips, or warnings |
| P6-041 | Add PostgreSQL tests | Concurrency, trigger, expiry, migration paths pass |
| P6-042 | Run Phase 1–5 regressions | No prior-phase regression |
| P6-050 | Complete report/evidence/audit | Atlas control set complete and attributable |
| P6-051 | Merge and post-merge verify | Master CI and local gates green on merge SHA |

## 10. Verification gates

### Fast gate

```bash
bash scripts/verify_phase6.sh
```

Must include:

- compilation;
- release-blocking Ruff checks;
- Phase 6 unit and registration tests;
- route and ARQ inventory;
- production deterministic-provider guards;
- migration graph and schema integrity;
- OpenAPI drift check;
- Phase 1–5 fast regressions;
- Atlas path validation.

### PostgreSQL gate

```bash
bash scripts/verify_phase6_postgres.sh
```

Must include:

- clean upgrade to Phase 6 head;
- upgrade from Phase 5 head;
- reserve/finalize idempotency;
- budget block with concurrent reservations;
- expiry release;
- append-only trigger;
- downgrade to Phase 5 and re-upgrade;
- Phase 1–6 PostgreSQL regressions;
- zero database-gated skips.

### Expected migration head

```text
20260615_1500_p6_ai_ops
```

## 11. Evidence requirements

Create:

```text
docs/roadmap/execution/atlas/phase_06_implementation_report.md
docs/release-evidence/atlas/phase-06/phase_06_evidence_index.md
docs/release-evidence/atlas/phase-06/phase_06_audit_report.md
docs/release-evidence/atlas/phase-06/raw/
```

Raw evidence must include:

- environment and exact Python version;
- branch, base SHA, candidate SHA, merge SHA when available;
- fast and PostgreSQL verifier output;
- migration graph and schema integrity;
- route and ARQ inventory;
- OpenAPI check;
- test counts, warnings, skips, and exit codes;
- SHA-256 manifest.

The collection script must not mark the audit Pass or the phase complete.

## 12. Rollback and recovery

Rollback triggers:

- budget overspend under concurrency;
- duplicate usage events;
- incorrect reserved-token release;
- mutable usage evidence;
- tutor regression or unsafe fallback;
- migration corruption;
- deterministic provider active in production.

Recovery:

1. Disable governed AI operations if durable accounting is not trustworthy.
2. Preserve usage events and reservations for investigation.
3. Roll application code back to the previous release.
4. Prefer forward-fix migrations if downgrade risks evidence loss.
5. Reconcile pending reservations by operation id.
6. Re-run all Phase 1–6 gates before restoration.

## 13. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Concurrent overspend | High | Locked counters and PostgreSQL integration tests |
| Reservation leak | High | TTL, scheduled expiry, operations view |
| Double finalization | High | Unique operation/reservation constraints and idempotency |
| Provider pricing drift | Medium | Versioned estimates; explicitly non-billing |
| Sensitive metadata | High | Metadata allow-list and no prompt/completion storage |
| Redis/DB divergence | Medium | PostgreSQL declared authoritative |
| Test environment uses deterministic provider | Medium | Explicit test-only guard |
| Evidence self-approval | High | Collector emits Pending audit only |

## 14. Start gate

- [ ] `PHASE_06_START_APPROVED=true`.
- [ ] Approval table completed.
- [ ] Plan committed.
- [ ] Worktree clean.
- [ ] Phase 5 Verified Complete.
- [ ] Phase 5 Atlas control set exists.
- [ ] Base SHA recorded.
- [ ] Limits approved.
- [ ] Migration and rollback reviewed.
- [ ] Evidence and audit scope accepted.

### Approval table

| Role | Name | Decision | Date | Reference |
|---|---|---|---|---|
| Phase owner | | Approve / Reject | | |
| Engineering approver | | Approve / Reject | | |
| Operations owner | | Approve / Reject | | |
| Security/privacy reviewer | | Approve / Reject | | |
| Evidence custodian | | Ready / Not ready | | |
| Planned auditor | | Scope accepted / Changes required | | |

## 15. Closure gate

Phase 6 may be marked `Verified Complete` only when:

- [ ] all mandatory implementation items are complete;
- [ ] fast and PostgreSQL gates pass with no unexpected skip;
- [ ] Phase 1–5 regressions pass;
- [ ] append-only evidence and budget concurrency are independently reproduced;
- [ ] implementation report reconciles the plan;
- [ ] evidence pack is complete and hashed;
- [ ] independent audit issues Pass or Pass with non-blocking observations;
- [ ] no Critical or High finding remains;
- [ ] feature branch is merged;
- [ ] post-merge verification passes on the merge SHA;
- [ ] status register is updated last.

### Closure approval

| Role | Name | Decision | Date | Reference |
|---|---|---|---|---|
| Phase owner | | Recommend close / Keep open | | |
| Engineering approver | | Approve / Reject | | |
| Operations owner | | Approve / Reject | | |
| Security/privacy reviewer | | Approve / Reject | | |
| Independent auditor | | Pass / Pass with observations / Fail | | |
| Release manager | | Merge/CI verified / Not verified | | |
| Final approver | | Verified Complete / Not complete | | |
