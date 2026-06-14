# Phase 1 Remediation Tracker

**Phase:** 1 — Batch AI Content Generation  
**Audit Date:** 2026-06-14  
**Verdict:** Verification Failed / Remediation Required  
**Document Version:** 1.0  
**Last Updated:** 2026-06-14

---

## Remediation Status Summary

| Severity | Findings | Open | In Progress | Closed |
|---|---|:---:|:---:|:---:|
| **Critical** | 2 | 2 | 0 | 0 |
| **High** | 7 | 7 | 0 | 0 |
| **Medium** | 3 | 3 | 0 | 0 |
| **Total** | 12 | 12 | 0 | 0 |

---

## Critical Findings (Must Fix Before Re-Audit)

### P1-R01 — Canonical Content Factory LLM Provider Remains Disabled

| Field | Value |
|---|---|
| Finding ID | P1-R01 |
| Severity | Critical |
| Description | The existing `LLMContentGenerationProvider` in `app/services/content_generation/providers/llm.py` still raises `RuntimeError("LLM content generation provider is not configured.")`. The Phase 1 overlay creates a parallel batch-generation path instead of completing the repository's existing canonical Content Factory provider. |
| Phase Objective Not Met | Yes — canonical Content Factory LLM mode remains non-functional |
| Required Action | Choose one: (1) Adapt `LLMContentGenerationProvider` to call the approved provider router, strict validator, safety controls, and prompt registry; then make new API use `ContentGenerationExecutor`. (2) Formally replace the existing executor/provider architecture, migrate all callers, remove/deprecate old path, and record in ADR. |
| Test Required | End-to-end test proving `CONTENT_FACTORY_GENERATION_ENABLED=true` and `CONTENT_FACTORY_PROVIDER=llm` executes normal Content Factory run and persists attributable pending-review artifact. |
| Owner | TBD |
| Target Date | TBD |
| Status | **OPEN** |

### P1-R02 — Alembic Revision-Length Monkeypatch Unsafe

| Field | Value |
|---|---|
| Finding ID | P1-R02 |
| Severity | Critical |
| Description | New revision identifier `20260614_0900_phase1_validation_reports` is 39 characters. Alembic's default `alembic_version.version_num` is VARCHAR(32). The monkeypatch in `alembic/env.py` only affects new tables, not existing columns in staging/production. |
| Deployment Risk | Migration can fail on existing databases |
| Required Action | 1. Rename revision to 32 chars or fewer (e.g., `20260614_0900_p1_validation`) in migration filename, `revision`, and all references. 2. Remove the monkeypatch. 3. Test both: (a) clean database → `alembic upgrade head`, (b) existing stamped database → upgrade. |
| Test Required | Both clean-database and existing-head upgrade paths must pass |
| Owner | TBD |
| Target Date | TBD |
| Status | **OPEN** |

---

## High Findings

### P1-R03 — Not Merged to Canonical Branch

| Field | Value |
|---|---|
| Finding ID | P1-R03 |
| Severity | High |
| Description | Work committed on `feature/phase-1-integration`, not merged to canonical branch. No PR URL, merge SHA, post-merge CI, or clean worktree evidence provided. |
| Governance Violation | Programme rules require canonical merge + post-merge CI before closure |
| Required Action | Merge through PR, run post-merge CI, regenerate evidence against merge commit, update implementation report with merge SHA, reissue audit |
| Owner | TBD |
| Target Date | TBD |
| Status | **OPEN** |

### P1-R04 — Provider Architecture Duplication

| Field | Value |
|---|---|
| Finding ID | P1-R04 |
| Severity | High |
| Description | Multiple overlapping provider abstractions exist: `app/services/llm_provider.py`, `app/services/llm/json_completion.py`, `app/services/llm/gateway.py`, `app/services/content_generation/providers/llm.py`, `app/modules/lessons/llm_gateway_v2.py`, `app/core/llm_gateway.py` |
| Impact | Inconsistent policies, duplicate code, hard-to-audit boundaries |
| Required Action | Create/update ADR identifying one canonical provider gateway for batch generation. Adapt other layers or deprecate alternatives. Add import/boundary test preventing additional abstractions. |
| Owner | TBD |
| Target Date | TBD |
| Status | **OPEN** |

### P1-R05 — Azure-Primary Strategy Not Implemented

| Field | Value |
|---|---|
| Finding ID | P1-R05 |
| Severity | High |
| Description | Accepted provider strategy specifies Azure OpenAI as primary with Anthropic/Groq fallback. New `build_provider_router()` supports Anthropic, Groq, Deterministic — but NOT Azure OpenAI. |
| ADR Non-Compliance | Implementation contradicts accepted architecture decision |
| Required Action | Either add Azure OpenAI adapter with structured-output support, timeout/error normalization, telemetry, and fallback tests, OR amend ADR through approved change control before closure. |
| Owner | TBD |
| Target Date | TBD |
| Status | **OPEN** |

### P1-R06 — Queue/Run Status Race Condition

| Field | Value |
|---|---|
| Finding ID | P1-R06 |
| Severity | High |
| Description | API flow: (1) create run with status `created`, (2) enqueue ARQ job, (3) set status to `queued`, (4) commit. Worker can complete run between (2) and (3), then stale API object overwrites terminal state as `queued`. |
| Production Impact | Incorrect run state persisted |
| Required Action | Use one of: (a) set `queued` before enqueue, change to `enqueue_failed` if queueing fails; (b) transactional outbox; (c) conditional update only allowing `created → queued`, refusing later states. Add concurrency regression test. |
| Owner | TBD |
| Target Date | TBD |
| Status | **OPEN** |

### P1-R07 — Source Snapshot Not Enforced

| Field | Value |
|---|---|
| Finding ID | P1-R07 |
| Severity | High |
| Description | Run creation stores source snapshot hash, but worker re-queries sources without comparing current hash to expected hash. Source can change between queue and execution. |
| Reproducibility Issue | Artifact may represent different source state than approved at run creation |
| Required Action | Use immutable source-version IDs OR compare `expected source_snapshot_hash` vs `resolved source_snapshot_hash` and fail task on mismatch. Add tests for: source changed after queue, approval removed, chunk deleted, source replaced. |
| Owner | TBD |
| Target Date | TBD |
| Status | **OPEN** |

### P1-R08 — Internal Source-Bundle Bypass

| Field | Value |
|---|---|
| Finding ID | P1-R08 |
| Severity | High |
| Description | `BatchGenerationEngine.process_run()` accepts `sources_by_caps_ref: dict[...] | None`. When supplied, `_resolve_sources()` uses it instead of querying approved source records. |
| Security Boundary Bypass | Server-authority over source selection can be bypassed |
| Required Action | Remove parameter from production engine API. For tests, inject `SourceContextService` fake rather than source text directly. |
| Owner | TBD |
| Target Date | TBD |
| Status | **OPEN** |

### P1-R09 — Circuit Breaker Not Durable

| Field | Value |
|---|---|
| Finding ID | P1-R09 |
| Severity | Medium |
| Description | `build_provider_router()` creates new router with in-memory circuit breakers per request/job. State disappears between jobs/processes. |
| Operational Value | Limited — only prevents repeated calls within single request |
| Required Action | Either document as request-local retry guard OR persist provider health/circuit state in Redis/shared service. Add operational metrics and outage test spanning multiple jobs. |
| Owner | TBD |
| Target Date | TBD |
| Status | **OPEN** |

---

## Medium Findings

### P1-R10 — Focused Tests Miss Canonical Path

| Field | Value |
|---|---|
| Finding ID | P1-R10 |
| Severity | Medium |
| Description | 97 tests are useful but mostly unit/orchestration. Missing: existing Content Factory executor in LLM mode, real HTTP with admin auth/DB/Redis/ARQ, queue/run concurrency race, source mutation, upgrade from existing head, full regression, OpenAPI drift, dependency-boundary checks. |
| Required Action | Add targeted integration tests and run full applicable repository gate before closure. |
| Owner | TBD |
| Target Date | TBD |
| Status | **OPEN** |

### P1-R11 — answer_key_verified Overstated

| Field | Value |
|---|---|
| Finding ID | P1-R11 |
| Severity | Medium |
| Description | Artifact persistence sets `answer_key_verified = content_type == "diagnostic_item"` — every diagnostic item labelled verified because of type, not independent verification. |
| Required Action | Set field only after actual answer-key verification step, or rename to represent schema consistency. |
| Owner | TBD |
| Target Date | TBD |
| Status | **OPEN** |

### P1-R12 — Audit Evidence Not Independently Attributable

| Field | Value |
|---|---|
| Finding ID | P1-R12 |
| Severity | Medium |
| Description | Walkthrough says audit report has Pass, but report not attached. Local `file://` links not portable. Missing: merge SHA, branch state, exact command outputs, versions, Docker digest, raw test outputs, hashes, auditor identity/declaration. |
| Required Action | Evidence pack should include: merge commit SHA, branch/clean-worktree state, exact command output/exit codes, Python/dep/Docker/PostgreSQL/Alembic versions, image digest, migration head before/after, raw 95/2 and 97/0 outputs, file hashes, auditor name/role/independence declaration. |
| Owner | TBD |
| Target Date | TBD |
| Status | **OPEN** |

---

## Required Closure Actions Summary

Before Phase 1 can be marked **Verified Complete**, all of the following must be addressed:

1. [ ] **P1-R01:** Replace or integrate existing `LLMContentGenerationProvider`; prove canonical Content Factory path works
2. [ ] **P1-R02:** Remove Alembic monkeypatch, shorten revision ID to ≤32 chars, test both upgrade paths
3. [ ] **P1-R03:** Merge through PR, run post-merge CI, regenerate evidence against merge commit
4. [ ] **P1-R04:** Consolidate duplicate provider architecture; create/update ADR
5. [ ] **P1-R05:** Add Azure OpenAI support or amend accepted ADR
6. [ ] **P1-R06:** Fix queue/run status race condition
7. [ ] **P1-R07:** Enforce immutable or hash-checked source snapshots
8. [ ] **P1-R08:** Remove supplied-source bypass from production engine
9. [ ] **P1-R09:** Document or persist circuit breaker state
10. [ ] **P1-R10:** Add E2E HTTP+PostgreSQL+Redis+ARQ verification; run full regression
11. [ ] **P1-R11:** Fix `answer_key_verified` field logic
12. [ ] **P1-R12:** Reissue audit with attributable evidence

---

## Governance Note

Per the programme's four-artefact control set requirements:
- Phase 1 remains at **Verification Failed / Remediation Required**
- Do not start Phase 2 as sole engineering WIP until Phase 1 critical findings are resolved OR an approved dependency decision explicitly permits limited parallel planning without treating Phase 1 as complete
- All 12 findings require resolution before re-audit

---

**Document Owner:** Release Manager  
**Next Review:** When all Critical findings are resolved  
**Re-Audit Target:** TBD pending remediation progress