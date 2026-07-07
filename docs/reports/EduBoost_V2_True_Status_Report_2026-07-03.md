---
title: "EduBoost V2 True Status Technical Report"
status: historical-superseded
owner: engineering
reviewers: [engineering, architecture, product]
audience: developer
source_of_truth: false
supersedes: []
superseded_by:
  - docs/current_state.md
  - docs/roadmap/production_readiness/production_readiness_register.json
  - docs/roadmap/production_readiness/current_state_documentation_truth_map.json
  - docs/roadmap/reconciliation/final_roadmap_reconciliation_closure_record.json
  - docs/roadmap/knowledge_graph/kg_roadmap_closure_record.json
last_reviewed: 2026-07-03
quarantined_by: PRD-0.2
quarantine_reason: "Historical audit report predates RR closure, KG closure, KG-ACT-001 runtime authority activation, KG-8 closure, and PRD-0.1 canonical current-state refresh."
review_interval_days: null
evidence_command: "n/a — historical report, superseded by current-state authority records"
code_anchors: [app/api_v2.py, docs/current_state.md, docs/roadmap/reconciliation/outstanding_work_register.md]
---


> **Historical report — superseded**
>
> This report is retained for audit history only. It is **not** a live roadmap, release, KG, RR, PRD, production-readiness, public-beta, billing, deployment, or runtime-authority source of truth.
>
> It predates the final RR closure, KG roadmap closure through KG-8, KG-ACT-001 controlled runtime KG authority activation, KG roadmap closure report, PRD-0.0 production-readiness stream authority, and PRD-0.1 canonical current-state documentation refresh.
>
> Current authority must be taken from `docs/current_state.md`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/roadmap/production_readiness/current_state_documentation_truth_map.json`, `docs/roadmap/reconciliation/final_roadmap_reconciliation_closure_record.json`, and `docs/roadmap/knowledge_graph/kg_roadmap_closure_record.json`.
>
> Do **not** use historical RR/KG status tables in this report to decide current implementation order.

# EduBoost V2 — True Status Technical Report

**Date:** 2026-07-03
**Snapshot audited:** `Eduboost-V2-master_44_.zip` (uploaded archive, no `.git` history included)
**Auditor stance:** independent, evidence-first review — documentation and prior audits are treated as claims to verify, not as ground truth.
**Templates consulted:** `docs/architecture/CORE_TECHNICAL_AUDIT_2026-05-17.md`, `reports/technical_state_vs_documentation_claims_2026-05-10.md`, `docs/roadmap/execution/technical_audit_remediation/true_state_application_audit_2026-06-29.md`, `audits/deep_app_audit/implementation_reality_report.md`

## Method and Limitations

This report was produced by static, code-level inspection of the uploaded repository snapshot, cross-checked against the project's own recent internal audits. It is **not** a repeat of the live-checkout methodology those prior audits used, and the differences matter:

- No `.git` directory was included in the archive, so branch, HEAD SHA, and commit-history claims below are inherited from the most recent internal audit documents, not independently re-derived.
- No PostgreSQL or Redis instance was available, so `/ready` and `/v2/health/deep` were not re-probed live. The June 29 internal audit already found both return `503` without a live database, and nothing in this snapshot suggests that has changed.
- The full third-party dependency set (FastAPI, SQLAlchemy, Anthropic/OpenAI SDKs, Azure SDKs, etc.) was not installed, so `app.api_v2:app` was not re-imported live. Instead, every file under `app/` and `scripts/` was compiled with `py_compile` (syntax-level proof only) and specific files implicated in prior audits were read directly to check whether the reported defects still exist in code.
- Route counts, duplicate-class findings, and specific line numbers below were independently re-derived from the current snapshot using `grep`/`ast`-level search, not copied from prior reports, except where explicitly marked as inherited.
- CI, hosted-run provenance, and branch-protection claims cannot be independently verified from a static archive; where this report relies on them it says so and attributes the claim to its source document.

Where this report says a finding is "verified in this audit," it means the underlying code was read directly in this session. Where it says a finding is "inherited," it means it comes from a dated internal document that could not be independently re-run here.

## Executive Summary

EduBoost V2 has made **real, verifiable progress** since the last deep architectural audit (2026-05-17). Every P0 defect that audit identified in the authentication and POPIA-consent request paths — undefined names in `auth.py`, dummy token responses, mismatched consent repository/service wiring, random (non-JWT) actor IDs on POPIA audit events, and dynamic `__import__`-based repository access in eight routers — was checked directly in this snapshot and is **fixed**. Two of the three P0 placeholders flagged by the project's own June 2 deep-application audit (the LLM content-generation provider, and the POPIA legal-hold/export-offered erasure checks) are also **now implemented for real**, not stubbed.

At the same time, the project's own governance system — the `RR-###` roadmap-reconciliation register — is the most reliable current source of truth, and it is candid that the programme is **not production-ready, not beta-release-ready, and not authorized for deployment, a release tag, or public traffic**. That boundary is stated consistently and without exception across every reconciliation record checked in this audit.

Three findings from this audit are worth flagging as newly or freshly documented, because they are not prominently stated together anywhere in the existing documentation set:

1. **Phase 2 (Semantic Retrieval) is implemented but not wired into the runtime.** A real ~1,500-line `pgvector`-backed retrieval package exists (`app/services/semantic_retrieval/`) with a genuine Alembic migration, and it is consumed by the content-generation grounding path. But it has no HTTP router, no entry in `app/core/config.py`, no `docker-compose.yml` service/env wiring, and only one narrow unit-test file covering the embedding provider alone. The historical `docs/roadmap/PHASE_STATUS_REGISTER.md` marks Phase 2 as "Complete," which overstates the current integration depth.
2. **A recorded coverage baseline shows 0% line coverage.** `docs/roadmap/reconciliation/rr_003_coverage_ci_route_authority_record.json` records `coverage_baseline_percent: 0.0` across 30,959 valid lines, caused by a pre-existing test-collection blocker, and the recorded coverage **threshold** for that baseline was also set to `0.0`, which makes the check pass trivially rather than proving anything about code quality. The project's own `docs/current_state.md` (dated 2026-07-02) already discloses this, but it is easy to miss inside a governance record.
3. **The "recorded"/"reconciled" status used throughout the RR register is a documentation-and-evidence-presence status, not a runtime-verified status**, and the project's own current-state document says so explicitly for RR-003 and RR-006. This is the same pattern the May 10 and May 17 audits warned about, and it persists — the project has gotten better at *disclosing* the gap but has not closed it.

The most accurate one-line summary of true status, synthesizing this audit with the project's own most recent records: **EduBoost V2's backend and frontend runtimes are demonstrably more coherent and further along than they were in May 2026, several real P0 defects have been genuinely fixed rather than papered over, but release-readiness claims remain governance-recorded rather than runtime-proven in several places, and the project itself continues to correctly withhold production, deployment, release-tag, and public-beta authorization.**

## Programme Status At A Glance

Per `docs/roadmap/PHASE_STATUS_REGISTER.md` (v3.0, 2026-07-02) and `docs/roadmap/reconciliation/roadmap_reconciliation_record.json`, the historical Atlas phase register (Phases 0–8) is retained for history only and is **no longer the active implementation queue**. The active queue is the `RR-###` outstanding-work register.

| Control | Value | Source |
|---|---|---|
| Production release authorised | **false** | every RR record JSON checked in this audit, unanimous |
| Deployment authorised | **false** | same |
| Release tag authorised | **false** | same |
| Public beta authorised | **false** | same |
| Runtime knowledge-graph implementation claimed | **false** | same |
| New unreconciled work authorised | **false** | `roadmap_reconciliation_record.json` |
| Reconciliation owner | Nkgolo Lebelo | `roadmap_reconciliation_record.json`, `rr_003`/`rr_006` records |

### RR register status (as recorded by the project itself)

| ID | Priority | Area | Recorded status | Caveat disclosed by the project |
|---|---:|---|---|---|
| RR-001 | P0 | Atlas phase reconciliation | Reconciled | — |
| RR-002 | P0 | Privacy / POPIA completion | Recorded | — |
| RR-003 | P0 | Coverage / CI / route authority | Recorded | **Coverage baseline recorded at 0.0%** because full test collection had pre-existing blockers |
| RR-004 | P1 | Workspace hygiene | Recorded | — |
| RR-005 | P1 | Technical debt burn-down | Valid | Duplicate service/repository classes still present in code (see Findings) |
| RR-006 | P0 | Security posture deepening | Recorded | Evidence PR merged with **only the required branch-protection check** blocking; other non-required CI checks were red |
| RR-007 | P1 | Product quality gates | Recorded | — |
| RR-008 | P0 | Operational readiness | Recorded | — |
| RR-009 | P1 | Governance/process reconciliation | Recorded | — |
| RR-010 | P0 | Beta outcome reporting (real learner feedback) | **Outstanding** | No beta observation period has occurred yet |
| RR-011 | P1 | Live billing provider integration | In progress, sandbox-only | Explicitly excludes live payments; last reviewed 2026-07-03 |
| RR-012 | P1 | Production telemetry dashboard | Outstanding | — |
| RR-013 | P2 | Advanced mastery-model research | Outstanding (backlog) | — |
| RR-014 | P2 | Public beta expansion | **Explicitly blocked** | Blocked until controlled-beta outcome exists |
| RR-015 | P0 | External approvals (security, POPIA/privacy, legal, CAPS/content, release sign-off) | **Outstanding** | — |
| RR-016 | P0 | Operational drills (backup/restore/rollback/incident) | **Outstanding** | Some rollback/support docs exist, but drills lack executable proof |
| RR-017 | P0 | Production deployment blockers (safety rails) | Preserved | Intentionally still blocking |
| RR-018 | P1 | Trustworthy-beta product features (feedback/report button, correction workflow) | Outstanding | — |

Read plainly: the P0 items still fully open are **RR-010 (beta outcome), RR-015 (external approvals), and RR-016 (operational drills)**. Those three, not architecture debt, are the largest remaining distance to any real release decision.

## What Changed Since the Last Two Deep Audits

The project has two prior code-level audits in its own history: `CORE_TECHNICAL_AUDIT_2026-05-17.md` (deep architecture review) and `true_state_application_audit_2026-06-29.md` (live-checkout runtime verification, 43 days later). This audit is a third data point, roughly one to five days after the second.

### P0 findings from the May 17 audit — verified in this session

| May 17 finding | Verified current state (this audit) |
|---|---|
| `app/api_v2_routers/auth.py` referenced `get_db`, `AsyncSession`, and other names without importing them; app import was broken | **Fixed.** `auth.py` now explicitly imports `AsyncSession` from `sqlalchemy.ext.asyncio` and `get_db` from `app.core.database` at the top of the file; all six `Depends(get_db)` usages resolve. |
| Auth router called `AuthService()` with no injected dependencies; returned dummy tokens | **Fixed and superseded.** The router now imports `AuthApplicationService` from `app.services.auth_application_service` via a dependency provider (`app.api_v2_deps.auth_service.get_auth_application_service`). The old ambiguous `AuthService()` construction is gone from the router. |
| `app/api_v2_routers/popia.py` wired the SQLAlchemy router to an asyncpg-shaped `ConsentService`/`AuditRepository` pair with incompatible method names | Not independently re-verified end-to-end without a live DB, but the router-level symptom described (mismatched construction) is no longer present in the file as read. |
| POPIA consent routes generated random UUID actor IDs instead of using the authenticated identity (`TODO: replace with real auth dependency`) | **Fixed.** `popia.py` now calls `_authenticated_actor_id(current_user)` for every grant/deny/withdraw/renew action; no `uuid4()` actor generation remains in the file. |
| Lesson read/complete/sync routes lacked ownership/consent enforcement | Not re-verified line-by-line in this session; flagged for the next audit pass. |
| Eight routers used `__import__(...)` to dynamically pull repositories, bypassing `.importlinter` boundary rules | **Fixed.** `parents.py`, `popia.py`, `diagnostics.py`, `study_plans.py`, `gamification.py`, `learners.py`, `consent.py`, and `onboarding.py` were each checked; zero `__import__` calls remain in any of them. |
| `app/core/authorization.py` defined `assert_can_access_learner` twice, with the second silently overriding the first | **Still present**, but now explicitly acknowledged in-line: the second definition (line 322) carries `# noqa: F811 — later def shadows this; kept for backward compat`. The duplication itself is unresolved; only the documentation of it has improved. |
| Duplicate canonical `AuthService`, `ConsentService`, `DiagnosticSessionService`, `AuditRepository`, `LearnerRepository`, `LessonRepository` classes across `app/modules/` and `app/repositories/`/`app/services/` | **Still present at the class level**, but demonstrably less dangerous: the legacy `AuthService` in `app/services/auth_service.py` is now labeled with `Compatibility settings hook used by legacy unit tests` and a `_compat_*` naming convention, and is not imported by any router. This is real progress from "which one is canonical is ambiguous" to "the legacy ones are labeled and unused by live routes," but the files have not been deleted or moved to `app/legacy`/`app/compat` as the May audit recommended. |

### Findings from the June 29 live-checkout audit — status as of this snapshot

The June 29 audit (`true_state_application_audit_2026-06-29.md`) is the most recent *live-execution* evidence available (it ran the app, the test suite, and the frontend toolchain against a real checkout). This snapshot cannot re-run those checks, so the following are **inherited, not re-verified**, and are presented with that caveat:

- Backend canonical and legacy entrypoints imported successfully (`app.api_v2:app` — 421 routes; `app.legacy.api.main:app` — 422 routes). This snapshot's static route-decorator count (211 `@router.*` decorators across `app/api_v2_routers/`, registered through a single loop that mounts each router under both `/api/v2` and `/v2`) is consistent with that figure (211 × 2 ≈ 422).
- OpenAPI generation was current (no drift) as of June 29.
- Frontend install, env-check, type-check, lint, unit tests, and production build all passed as of June 29 (Next.js 16.2.7, 24 statically generated pages).
- Mocked Playwright learner/parent journeys passed as of June 29. This proves mocked frontend flows only, not backend-backed E2E.
- `make test-fast` **failed** on June 29 with 7 failures out of 2,375 collected tests (2,367 passed, 11 skipped, 1 xfailed). All 7 failures were in **governance/verifier contract tests** (e.g. `test_phase02k_verifier_assets_are_present`, `test_e2e_playwright_authority_verifier_passes`), not ordinary business-logic tests — the pattern was that historical remediation-phase verifiers still expected an "active slice" state that no longer exists after the remediation stream closed.
- The hosted CI authority verifier failed on June 29: the recorded `head_sha` in the authority record did not match either the current branch HEAD or the raw GitHub Actions run's `headSha`. The June 29 report calls this "the most important provenance issue found in the audit." This snapshot cannot confirm whether it has since been resolved; it should be treated as open until a fresh CI-authority verification is run.
- Local `/ready` and `/v2/health/deep` returned `503` on June 29 because Postgres and Redis were not running in that audit environment — an environment limitation, not necessarily a code defect, but it means full-stack readiness has not been proven outside Docker Compose.

## Deep-Application-Audit Placeholder Findings — verified in this session

The project's own `audits/deep_app_audit/implementation_reality_report.md` (2026-06-02, explicitly cited in `README.md` as "the active deep-audit baseline") flagged nine classification findings. This audit re-checked the three P0 items directly against current code:

| ID | June 2 finding | Verified current state |
|---|---|---|
| DA-P0-001 | `app/services/content_generation/providers/llm.py` raised `RuntimeError` for all generation methods — a placeholder | **Fixed.** The provider now builds real prompts, calls a provider router (`build_provider_router`), parses structured JSON responses, and runs a safety filter. Two out-of-scope methods (`generate_assessment_blueprint`, `generate_study_plan_template`) now raise an honest `NotImplementedError` with an explicit "outside the Phase 1 launch scope" message, rather than pretending to work. |
| DA-P0-002 | `app/services/popia_service.py` hard-coded `legal_hold=False` and `export_offered=False` in erasure preflight | **Fixed.** A new module, `app/services/popia_erasure_safety.py` (RR-002), computes `legal_hold` from six real learner-record attributes (`legal_hold`, `legal_hold_active`, `retention_hold`, `billing_hold`, `school_retention_hold`, `investigation_hold`) via `learner_has_legal_hold()`, and `execute_erasure()` blocks on both legal hold and unsatisfied export requirements before allowing erasure. |
| DA-P0-003 | `scripts/run_database_backup.py`/`run_database_restore.py` were "not implemented in this scaffold" outside dry-run | Reported fixed as of the June 2 document's own "Phase 2 Remediation Update" (guarded real `pg_dump`/`pg_restore`/`psql` execution paths added). Not independently re-verified in this session because it requires a live database to exercise safely. |
| DA-P1-004 | `app/services/etl/etl_pipeline_v2.py` stored only the first embedding element and exposed a `semantic_search_stub()` | **Partially superseded, not resolved.** See "Semantic Retrieval (Phase 2)" below — a real, separate retrieval package now exists, but the *original* stubbed code path (`semantic_search_stub`, still present and still called at `etl_pipeline_v2.py:649`) was not removed or replaced in-place. |
| DA-P1-005 | Learner content reads defaulted to include unsupported legacy fallback | Reported fixed in the June 2 document ("now default to `production_only`"). Not independently re-verified in this session. |
| DA-P1-006 | Frontend Content Factory mock dashboard had no production guard | Reported fixed in the June 2 document ("blocked when `NODE_ENV=production`"). Not independently re-verified in this session. |
| DA-P1-007 | Auth compatibility surface had duplicated token-store assignment | Reported partially fixed in the June 2 document; compatibility boundary intentionally retained. Consistent with this audit's own finding that legacy `AuthService` is now clearly labeled compat-only. |

## Fresh Finding: Semantic Retrieval (Phase 2) Is Implemented But Not Integrated

This is the most concrete gap this audit surfaced that is not clearly stated anywhere in the existing documentation set, and it is directly relevant to the Phase 2 (Semantic Retrieval and Grounding) work in progress.

**What exists and is real:**

- `app/services/semantic_retrieval/` — a genuine 1,503-line package: `embedding.py` (156 lines, includes a `DeterministicEmbeddingProvider` for CI plus a real provider path, and explicitly forbids the deterministic provider in production per its own test), `repository.py` (263 lines, raw-SQL ANN search with a PostgreSQL full-text-search fallback via `to_tsvector`), `indexing.py` (377 lines), `service.py` (171 lines), `evaluation.py`, `generation_context.py`, and `types.py`.
- `app/models/retrieval.py` — a real `pgvector`-typed column (`vector(EMBEDDING_DIMENSIONS)`) implemented without requiring the `pgvector-python` runtime dependency.
- `alembic/versions/20260614_1200_p2_retrieval.py` — a real, dated migration for the retrieval schema.
- `app/services/content_generation/source_context.py` imports `generation_context` from the semantic-retrieval package, so lesson/diagnostic generation prompts are, to some extent, already grounded by it.

**What is missing:**

- **No HTTP router.** Nothing under `app/api_v2_routers/` or in `app/api_v2.py` references `semantic_retrieval`, `RetrievalService`, or exposes a retrieval endpoint. The capability cannot currently be called directly over HTTP or inspected via `/docs`.
- **No settings surface.** `app/core/config.py` has zero references to `EMBEDDING` or `RETRIEVAL` — there is no environment-variable-driven way to choose an embedding provider, endpoint, or index configuration at runtime outside of what the package hard-codes or infers.
- **No `docker-compose.yml` wiring.** No `pgvector`, embedding-provider, or retrieval-specific service or environment variable appears in the default compose stack.
- **Thin test coverage.** Only `tests/phase02/test_embedding.py` exists (60 lines), and it covers exclusively the deterministic embedding provider's shape, token-sensitivity, and production-guard behavior. There is no test exercising `indexing.py`, `repository.py`'s ANN/full-text search, or `service.py` end-to-end.
- **The old stub is still live.** `app/services/etl/etl_pipeline_v2.py` still defines and calls `semantic_search_stub()` (line 583, called at line 649). The new package and the old stub currently coexist rather than the new one having replaced the old one.

**Why this matters:** `docs/roadmap/PHASE_STATUS_REGISTER.md` records Phase 2 (Semantic Retrieval) as historically "Complete / closure review in old register." Read casually, that suggests the capability is done. The code shows a substantial, well-structured implementation that is genuinely mid-integration — consistent with grounding being wired into one content-generation code path but not yet exposed, configured, containerized, or broadly tested. The accurate status is **"core retrieval logic implemented; production wiring (router, config, compose, test breadth) incomplete,"** not "complete."

## Claim vs. True State

| Area | Documentation / register claim | True state found in this audit | Assessment |
|---|---|---|---|
| Production/deployment/beta authorization | Every RR record explicitly says `false`/`unauthorised` | Consistent everywhere checked | **Accurate — the project correctly under-claims here.** |
| Auth router correctness | (implicit, via RR-001/RR-005 closure) | `get_db`/`AsyncSession` imports fixed; canonical `AuthApplicationService` now used | **True and improved since May.** |
| POPIA actor attribution | (implicit, via RR-002 closure) | Random UUIDs replaced with JWT-derived actor IDs | **True and improved since May.** |
| POPIA erasure legal-hold/export checks | RR-002 "Recorded"; June 2 audit flagged as hard-coded placeholders | Real attribute-based legal-hold check and export-satisfaction gate now implemented | **True and improved since June 2.** |
| Content-generation LLM provider | June 2 audit flagged as `RuntimeError` placeholder | Real prompt/response/safety pipeline now implemented | **True and improved since June 2.** |
| Semantic retrieval (Phase 2) | Historical register: "Complete" | Substantial implementation exists but has no router, no config surface, no compose wiring, and one narrow test file; old stub still coexists | **Overstated by the historical register; accurately hedged nowhere in a single place.** |
| Coverage baseline (RR-003) | "Coverage / CI / route authority — Recorded" | 0.0% of 30,959 valid lines covered in the recorded baseline; recorded threshold also 0.0% | **Technically "recorded," but the number itself signals a broken test-collection run, not a real coverage measurement. `docs/current_state.md` discloses this but it is easy to miss.** |
| Security posture (RR-006) | "Security posture deepening — Recorded," verification checks nearly all document-existence checks | `docs/current_state.md` itself discloses the evidence PR merged with only the required branch-protection check green; other non-required CI checks were red | **Recorded status reflects document/policy presence, not a fully green CI run — disclosed, but the RR-006 record's own `verification.checks` block reads as more reassuring than that caveat suggests.** |
| Duplicate service/repository classes (RR-005) | "Technical debt burn-down — Valid" | `AuthService`, `ConsentService`, `DiagnosticSessionService`, `AuditRepository`, `LearnerRepository`, `LessonRepository` still exist in duplicate across modules/services/repositories | **"Valid" register status coexists with unresolved duplication; the legacy copies are now labeled and unused by live routers, which is real progress, but the files were not removed or relocated as recommended in May.** |
| `app/core/authorization.py` duplicate function | Not claimed anywhere as fixed | Second `assert_can_access_learner` definition still silently shadows the first, now with a `noqa: F811` comment acknowledging it | **Known, documented, unresolved.** |
| Outstanding-work register per-item notes | Reads as if RR-001 through RR-009 work is still pending ("Register still says...", "canonical closure is not reconciled", etc.) | Individual RR record JSONs and `docs/current_state.md` (one day newer) show RR-001–RR-009 as recorded/closed | **Stale relative to newer per-item records — a minor instance of the exact documentation-drift pattern the project's own governance process exists to prevent.** |

## Repository Inventory Snapshot

Counts independently derived from this snapshot (tracked-file semantics may differ slightly from a live `git ls-files` count, since no `.git` metadata was present to distinguish tracked from ignored files):

| Area | Files | Lines |
|---|---:|---:|
| `app/` (`.py`) | 409 | 74,090 |
| `app/api_v2_routers/` | 32 | — |
| `app/frontend/src/` (`.ts`/`.tsx`) | 218 | — |
| `tests/` (`.py`) | 836 | 76,013 |
| `docs/` (`.md`) | 1,582 | — |
| `scripts/` (`.py`) | 833 | — |
| `alembic/versions/` | 49 migrations | — |
| `.github/workflows/` | 54 workflow files | — |
| `docs/adr/` | 57 ADRs | — |
| Route decorators (`app/api_v2_routers/`) | 211 distinct routes | mounted under both `/api/v2` and `/v2` (≈422 total registrations, consistent with the June 29 audit's live-imported count of 421/422) |

The scale itself is a finding: this is a large, actively maintained codebase with a genuinely unusual density of governance/evidence tooling (`docs/roadmap/execution/technical_audit_remediation/` alone contains over 30 phase/verifier documents). That density is a double-edged asset — it is why real defects get found and fixed (as this audit repeatedly confirmed), but it is also why "recorded" and "verified" are easy to conflate, both for readers and, per the project's own admissions, occasionally for the verifiers themselves.

## Risk Assessment

| Risk | Severity | Why it matters |
|---|---|---|
| Semantic retrieval (Phase 2) marked "Complete" historically while runtime wiring is absent | Medium | A future reader or the next work session could assume grounding is available end-to-end via an API when it is currently only reachable through one internal content-generation code path. |
| 0.0% recorded coverage baseline with a 0.0% threshold (RR-003) | High | If read out of context, "coverage baseline recorded" sounds like a real measurement was taken and a bar was set. In fact the number reveals a broken test-collection run, and the threshold was set to make the check pass regardless. |
| RR-006 evidence merged with non-required CI checks red | Medium | Security-posture "Recorded" status is currently closer to "policy documents exist and are checked for required phrases" than "security controls are proven green in CI." The project discloses this but the disclosure is easy to overlook inside a passing-looking verification block. |
| Duplicate canonical services/repositories not yet removed | Medium | Even though the dangerous wiring mismatches are fixed and legacy classes are now labeled, the underlying ambiguity (which class is "the" `AuditRepository`, etc.) remains a standing invitation for a future change to wire the wrong one again. |
| `assert_can_access_learner` duplicate definition | Medium | A reviewer reading the first definition is reading dead code; only the second definition executes. This is now commented, which helps, but the function itself has not been consolidated. |
| Hosted CI authority SHA mismatch (inherited from June 29) | High (if still open) | If unresolved, claims of "merge readiness" or "hosted CI success" for the current HEAD cannot be trusted without a fresh authority verification. This snapshot cannot confirm current status. |
| Outstanding-work register per-item notes are stale relative to newer RR record JSONs | Low | Minor internal inconsistency; does not misstate release authorization (which is consistently `false` everywhere), but could confuse a reader about which RR items are truly still open work versus already recorded. |
| Old ETL semantic-search stub still coexists with the new retrieval package | Low–Medium | Two retrieval code paths of very different maturity exist side by side; a future change could easily call the wrong one. |

## Recommended Next Steps

These are ordered to fit the project's own `RR-###` discipline — per `docs/roadmap/reconciliation/roadmap_new_work_freeze.md`, next work should cite an existing RR item rather than open a new unreconciled workstream. Where a finding from this audit does not cleanly map to an existing RR item, that is called out explicitly.

1. **Close the semantic-retrieval integration gap (maps to Historical Phase 2 / no current RR-### — recommend opening one under RR-005 technical-debt burn-down, or a new RR-019).** Add a router (even a minimal internal/admin-only one), wire `EMBEDDING_*`/`RETRIEVAL_*` settings into `app/core/config.py`, add the retrieval service to `docker-compose.yml`, retire `semantic_search_stub()` in `etl_pipeline_v2.py` in favor of the new package, and extend `tests/phase02/` to cover `indexing.py`, `repository.py`, and `service.py`, not just `embedding.py`.
2. **Re-baseline RR-003 coverage for real (RR-003 follow-up).** Diagnose and fix the "pre-existing blocker" that caused full test collection to fail during the coverage run, regenerate coverage against a clean collection, and set a non-zero, meaningful threshold rather than `0.0%`.
3. **Re-run the hosted CI authority verifier against current HEAD (RR-006/RR-003 follow-up).** Confirm whether the SHA mismatch found on June 29 is still present; if so, recapture CI evidence from a run whose `headSha` matches current HEAD, or make the authority record distinguish CI-run SHA from evidence-commit SHA explicitly.
4. **Consolidate duplicate canonical classes (RR-005).** Move the now-unused legacy `AuthService`, `ConsentService`, `DiagnosticSessionService`, and duplicate repository classes into `app/legacy`/`app/compat` as the May 17 audit recommended, or delete them if nothing still imports them.
5. **Fix the `assert_can_access_learner` duplicate definition (RR-005).** Keep one implementation; if a compatibility variant is genuinely needed, give it a distinct name as the `noqa` comment already implies it should have.
6. **Refresh `outstanding_work_register.md` per-item notes (RR-009).** The register's own "Current note" column for RR-001–RR-009 reads as open work; align it with the closure state already recorded in the individual RR JSON files and `docs/current_state.md`.
7. **Prioritize RR-010, RR-015, and RR-016.** These are the only fully-open P0 items in the register and are the actual remaining distance to any real release/beta decision — none of them are architecture work, and none of them are fixed by more code changes alone (they require an observed beta period, external sign-offs, and executed operational drills with evidence).

## Bottom Line

EduBoost V2 is a large, seriously engineered project with an unusually disciplined internal audit culture, and that discipline is visibly paying off: real P0 defects identified in May (broken auth imports, dummy tokens, mismatched POPIA wiring, random audit actor IDs, architecture-boundary-violating dynamic imports) and in June (a placeholder LLM provider, hard-coded POPIA legal-hold bypasses) were checked directly in this audit and are genuinely fixed, not just marked fixed. The project also correctly and consistently withholds production, deployment, release-tag, and public-beta authorization everywhere this was checked.

At the same time, "true status" is not simply "green." A concrete, well-built Phase 2 semantic-retrieval capability exists but is not yet reachable through the API, configured, containerized, or well-tested, despite a historical register entry calling it "Complete." A recorded coverage baseline of 0.0% and a matching 0.0% threshold currently satisfy a governance check without saying anything real about code quality. Duplicate canonical service/repository classes and one duplicate function definition remain unresolved, even though the dangerous parts of that ambiguity have been fixed. And the single most trustworthy sentence in the entire documentation set may be the project's own, in `docs/current_state.md`: *"This file is not a release approval... Release decisions must be made through the release source-of-truth documents and evidence commands."* That standard, applied here too, is the right one — this report should be read the same way: as evidence gathered on 2026-07-03, not as a release approval.

> **The safest current public claim:** EduBoost V2 has a substantially repaired, architecturally coherent V2 backend and a working frontend build/test pipeline, with several previously broken P0 request paths now genuinely fixed. It is not production-ready, beta-release-ready, or authorized for deployment or public traffic. The largest remaining gaps are an unintegrated but real semantic-retrieval capability, a governance-recorded rather than runtime-proven coverage/security baseline, and three fully open P0 items — a real beta observation period, external approvals, and executed operational drills — none of which close through further code changes alone.
