# EduBoost V2 True-State Technical Report

**Assessment date:** 2026-07-10  
**Checkout:** `/home/nkgolol/Dev/SandBox/Eduboost-V2-phase02r-gate2r1`  
**Branch:** `codex/prd-905-909-commercial-runtime-audit-remediation-handoff-evidence`  
**HEAD:** `ef775cfc41`  
**Comparison base:** local `origin/master` at `689145bf4d`  
**Overall verdict:** **RED — NO-GO for production, public beta, live learner traffic, live billing, or PRD-10 handoff**

## 1. Executive conclusion

EduBoost V2 is a large, actively developed modular-monolith codebase with substantial backend, frontend, curriculum, privacy, testing, deployment, and governance machinery. It is more than a prototype: both FastAPI entry points import, the canonical API exposes hundreds of routes, the Next.js production build completes, TypeScript passes, and focused mocked browser journeys pass.

It is not, however, in a trustworthy release-candidate state. The current branch and production-readiness records overstate closure. The most important current facts are:

- The live readiness probe returns **503 Service Unavailable** because Redis is absent.
- The live Supabase database is stamped with Alembic revision `20260531_1600`, which is not present anywhere in the repository's current migration graph.
- The ORM registers 98 tables, while the live database contains only 49 matching application tables. Fifty-four ORM tables are missing, including current assessment, study-plan, runtime-KG/curriculum, AI-usage, and tutor-persistence tables.
- The live `diagnostic_items` table is missing all four queried IRT fields: `irt_quality_state`, `irt_discrimination`, `irt_difficulty`, and `irt_guessing`.
- The backend unit gate is red. A bounded serial run stopped at 20 failures after 536 passes and 1 skip. A focused product/runtime selection had 5 failures and 53 passes.
- The integration profile had 2 failures, 6 passes, and 247 skips. Both failures are POPIA HTTP authorization-contract failures.
- Frontend lint fails on a conditional React hook. Vitest has 3 timeouts out of 150 tests. The production build nevertheless succeeds.
- The committed OpenAPI document and route inventory are stale.
- Python static quality is substantially red: 443 Ruff findings and 378 mypy errors across 100 source files. Import Linter's three narrow contracts pass.
- Dependency security is red: 87 known findings in the base lock, 46 in the ML lock, and 2 frontend production findings. The combined Python audit command in CI cannot resolve because base and ML locks pin different Jinja2 versions.
- The commercial runtime remediation endpoint returns `accepted: true`, `runtime_blockers_remediated: true`, and an empty blocker list from a constant dataclass. It does not evaluate runtime state. This contradicts the live 503 readiness result, schema divergence, and red tests.

The honest classification is therefore:

> **Buildable and partially testable; not green, not live-stack ready, not schema-aligned, not security-clean, not evidence-consistent, and not release-ready.**

## 2. Assessment boundary and method

This report does not accept roadmap records, generated reports, or checker output as proof by themselves. Claims were checked against source, executable commands, and the currently available local runtime.

Evidence gathered included:

- Git identity, branch divergence, worktree state, and diff against `origin/master`.
- FastAPI entrypoint imports and route enumeration.
- Alembic graph validation and direct read-only queries against the running Supabase PostgreSQL container.
- Direct ASGI probes of `/`, `/health`, `/ready`, and the commercial remediation endpoint.
- Backend unit and integration tests.
- Frontend dependency installation, TypeScript, ESLint, Vitest, production build, and Chromium Playwright journeys.
- Ruff, mypy, Black, Import Linter, Bandit, pip-audit, pnpm audit, and detect-secrets candidate scanning.
- Cross-checking `docs/current_state.md`, `docs/project_status.md`, the release no-go status, the production-readiness register, and the PRD-9.5-9.9 evidence implementation.

No production environment, remote CI run, branch-protection configuration, external legal approval, independent security review, backup/restore drill, or deployed staging environment was available in this checkout. Those areas remain unverified, not passed.

## 3. Repository and branch state

### 3.1 Current branch

The worktree was clean at the start. The current branch is four commits ahead of local `origin/master` and zero behind:

1. `ddcd5b1999` — commercial runtime blocker repair
2. `cdda204535` — remediation handoff evidence
3. `5116abc668` — PRD-9 audit expectation alignment
4. `ef775cfc41` — workspace hygiene mount ignore

The aggregate diff is unusually large: 336 files changed, 1,125 insertions, and 228,957 deletions. Most deletions are generated documentation builds, generated inventories, local logs, backups, coverage output, and temporary artifacts. Application changes are comparatively small and focus on assessment/auth repository compatibility and a deterministic PRD-9 remediation status surface.

### 3.2 Branch-specific evidence is not valid current proof

The branch records all of the following as true:

- `commercial_runtime_blockers_remediated`
- `subscription_runtime_contract_fixed`
- `assessment_runtime_contract_fixed`
- `repository_hygiene_repaired`
- `prd9_sequence_complete`
- `prd10_handoff_authorised`

The current verifier itself returns `authority_valid: false` and `valid: false` because its repository-hygiene assertion fails whenever ignored `logs/` or `temp/` paths exist. Those paths currently contain local seed and database-repeatability artifacts. More importantly, the verifier's positive runtime checks are mostly static text checks for method names and constructor strings. It does not start the stack, compare live schema to Alembic head, exercise billing, or execute a backend-backed commercial flow.

The remediation endpoint is also deterministic rather than diagnostic. `build_default_commercial_runtime_audit_remediation_report()` constructs an accepted report with no blockers regardless of database, Redis, tests, billing provider, or security state. The endpoint returned HTTP 200 and `runtime_blockers_remediated: true` during this audit while `/ready` returned HTTP 503 in the same process.

## 4. System architecture as implemented

### 4.1 Backend

The canonical backend is `app.api_v2:app`, a FastAPI modular monolith. A compatibility application remains at `app.legacy.api.main:app`.

Observed import/runtime surface:

- Canonical V2 application: 447 routes.
- Legacy compatibility application: 448 routes.
- Source route decorators: 236.
- Routers are mounted under both `/api/v2` and `/v2`, which roughly doubles the exposed route count.
- Root `/` is an API JSON response, not the frontend application.
- Cross-cutting components include request IDs, structured logging, timing, analytics, rate limiting, CORS, security headers, Prometheus metrics, Redis, PostgreSQL, and optional LLM-provider checks.
- Background work is intended to use ARQ, with a separate worker entrypoint.

The architectural direction is coherent, but the implementation is not consistently modular. Import Linter reports three configured contracts as kept, yet mypy reports 378 errors and Ruff reports 443 findings. The code contains compatibility loaders, duplicate service/repository families, dynamic constructor inspection, and legacy shims that make static contracts look cleaner than the real runtime dependency surface.

### 4.2 Data model and migrations

Repository-side state:

- 46 valid Alembic revisions.
- One repository head: `20260708_2100_prd2_runtime_kg`.
- 98 SQLAlchemy metadata tables after importing `app.models`.
- The database-free schema checker passes because it validates ORM metadata only.

Live local Supabase state:

- PostgreSQL container is healthy on port 54322.
- `alembic_version` contains `20260531_1600`.
- That revision cannot be located by Alembic and does not occur in source, migrations, tests, scripts, or docs.
- Live schema contains 50 public tables including `alembic_version`, of which 49 match application/legacy data tables.
- Fifty-four current ORM tables are absent.
- Five live tables are outside current ORM metadata: `consent_records`, `correction_requests`, `data_export_requests`, `erasure_requests`, and `restriction_requests`.

This is not a normal “a few migrations behind” condition. It is migration-history divergence. Running `alembic upgrade head` against this database without first reconciling lineage would be unsafe.

The readiness implementation incorrectly labels any non-`base` value in `alembic_version` as migration status `ok`; it does not compare the live revision to the repository head or even verify that the revision exists in the graph.

### 4.3 Frontend

The frontend is a Next.js App Router application under `app/frontend`.

Observed stack and surface:

- Next.js 16.2.7.
- React/React DOM 18.3.1.
- TypeScript 5.4.5.
- 219 TypeScript/TSX source files and roughly 19,141 source lines.
- Production build generated 24 static pages and a wider mix of static/dynamic/API routes.
- Browser-to-backend traffic primarily passes through Next server routes under `/api/backend`, which attach the server-side session token and proxy to the FastAPI service.
- A second Next-side tutor API implements safety, rate limiting, provider calls, and audit stubs independently from the FastAPI tutor route.

The production build succeeds, which is meaningful. However, there are transitional and duplicated behaviors:

- Learner layout calls `useEffect` conditionally after an early return, violating React's hook ordering rules.
- Onboarding explicitly tells the user that guardian consent still needs backend enforcement.
- The Next tutor API writes audit events through `auditEventStub` and returns `provider_unavailable` when no provider key is configured.
- The frontend keeps a development token fallback in browser local storage (`guardian_token`) in addition to the server-session path.
- Parent and legacy route aliases remain alongside the newer nested learner/parent paths.

### 4.4 Deployment and operations

The repository carries multiple operational targets and generations of deployment configuration:

- Development and production-like Docker Compose files.
- Azure Container Apps Bicep.
- Kubernetes manifests.
- Nginx, Prometheus, Alertmanager, Grafana, PostgreSQL, Redis, API, worker, and frontend configurations.
- A legacy Render configuration.

Documentation calls Azure Container Apps authoritative, but this audit found no currently running API, worker, Redis, or frontend service. Only the Supabase PostgreSQL container was active. No deployed Azure or staging state was verified.

## 5. Runtime truth

The application was probed in test mode against the running PostgreSQL container, with background consent processing disabled and no data-mutating endpoint called.

| Probe | Result | Meaning |
|---|---:|---|
| `/` | 200 | FastAPI root responds with JSON. |
| `/health` | 200 | Shallow process health only. |
| `/ready` | 503 | Critical Redis dependency unavailable. |
| PostgreSQL readiness component | `ok` | Basic `SELECT 1` succeeds. |
| Redis readiness component | `error: ConnectionError` | No Redis service is running. |
| Migration readiness component | incorrectly `ok` | Reports unknown revision `20260531_1600`. |
| Audit repository component | `ok` | `audit_events` can be queried. |
| LLM component | `skipped` | No provider credentials configured. |
| Commercial remediation endpoint | 200 / accepted | Static status contradicts live readiness. |

The health model therefore needs two corrections: exact migration-head/schema validation, and removal of status endpoints that declare remediation from constants rather than current evidence.

## 6. Functional implementation findings

### 6.1 Authentication and object authorization

Positive controls exist: JWT validation, production placeholder-secret rejection, role dependencies, route guards, and learner-write helper layers.

Material gaps remain:

- `app/security/authorization.py` contains guardian/learner and teacher/learner repository checks that are explicitly TODO placeholders and always return `False`.
- Auth and consent paths have multiple compatibility layers and dynamic helper discovery.
- The integration POPIA lifecycle tests receive 401 where 200 or 403 is expected.
- Mypy identifies concrete incompatibilities between the POPIA route, the consent dependency adapter, and the canonical consent service method signatures.
- The integration profile's broad skip behavior prevents most DB/Redis authorization behavior from being exercised unless a correctly prepared test database is supplied.

### 6.2 POPIA and data-subject rights

The repository contains extensive POPIA models, services, audit controls, route checks, and governance evidence. Static consent checkers all return PASS. That is not equivalent to runtime completion.

Current contradictory evidence:

- Two POPIA HTTP lifecycle integration tests fail.
- The consent route/service types do not agree under mypy.
- The live database contains both legacy and current consent/data-rights table families.
- The frontend has three timed-out user-flow tests, including a parent data-export action.
- Static checkers mostly verify imports, source tokens, route ordering, or generated inventories.

POPIA should be treated as implemented in parts but not end-to-end verified.

### 6.3 Billing and commercial launch

The billing router and Stripe service exist, with webhook persistence and subscription repository methods. It is not live-billing ready:

- Checkout currently passes the literal `billing-placeholder` instead of a decrypted guardian email.
- No live Stripe keys, checkout, webhook round trip, refund, invoice, tax, or entitlement transition was verified.
- Mypy reports that the injected `AuditService` lacks the `record` method used by the billing webhook route.
- The live database does not contain all current assessment and subscription-adjacent runtime tables expected by the code.
- The commercial readiness/remediation surfaces are deterministic policy reports, not provider or transaction probes.

### 6.4 Learning, diagnostics, curriculum, and AI

There is substantial implemented source for lessons, diagnostics, IRT, study plans, gamification, curriculum ingestion, content review, grounded generation, semantic retrieval, runtime knowledge graph, and AI-budget controls.

The true maturity varies sharply:

- Diagnostics and learner flows have meaningful unit/frontend coverage, but the live diagnostic schema is missing current IRT columns.
- Study-plan, assessment, AI-budget, tutor, and runtime-KG tables are missing from the live database.
- Source contains at least 11 TODO/FIXME markers and 34 `pass`/`NotImplementedError` occurrences; some are intentional exception types or optional fallbacks, while others are real deferred behavior.
- Content-generation code explicitly leaves assessment-blueprint and study-plan-template generation outside the Phase 1 scope.
- ETL v2 contains documented stubs such as one-element embedding storage and first-sentence summaries.
- Hugging Face model loading uses `trust_remote_code=True` without revision pinning.
- The frontend tutor route has stub audit behavior and a benign provider-unavailable fallback.

The correct statement is that the platform has broad foundations and several functional slices, not that every advertised learning/AI capability is production-backed.

## 7. Verification results

### 7.1 Backend tests

Collected test inventory:

- 3,645 unit tests.
- 255 integration tests.
- 15 Playwright spec/setup files.

Observed results:

| Suite | Result |
|---|---|
| Unit fast profile, serial, max 20 failures | 20 failed, 536 passed, 1 skipped, 914 deselected; stopped at max-fail. |
| Focused PRD-9 plus core service selection | 5 failed, 53 passed. |
| Integration fast profile | 2 failed, 6 passed, 247 skipped. |
| Migration graph | PASS: 46 revisions, one head. |
| Runtime import check | PASS: both FastAPI applications import. |
| Import Linter | PASS: 3 configured contracts. |
| Schema integrity script | PASS for ORM metadata only. |

The first 20 unit failures are dominated by evidence-state and roadmap reconciliation tests that still expect pre-capture/pending state after evidence has been captured, missing deleted generated inventory, and PRD-0-only register assumptions that no longer accept `PRD-9.5-9.9`. That reveals stale tests and state-machine design problems. It does not make the failures harmless: these tests are part of `tests/unit` and are not consistently marked `governance`, so they break the advertised fast gate.

The focused service failures include a learner service whose tests inject a mock repository positionally while the implementation treats the argument as a database session, then attempts to parse fixture IDs such as `learner-123` as UUIDs.

### 7.2 Frontend tests and build

| Check | Result |
|---|---|
| Frozen dependency install | PASS after installing 651 packages from `app/frontend/pnpm-lock.yaml`. |
| TypeScript | PASS. |
| ESLint | FAIL: 1 error and 75 warnings. |
| Vitest | 3 failed/timeouts, 147 passed. |
| Next production build | PASS. |
| Mocked learner/parent Chromium journeys | 4 passed after installing the Playwright Chromium runtime. |

The successful build and mocked journeys are credible positives. The mocked journeys validate frontend success and denial rendering only; they do not prove backend-backed auth, consent, database, diagnostic, billing, or learner-state flows.

### 7.3 Contract and generated-artifact drift

- `scripts/generate_openapi.py --check`: FAIL — committed OpenAPI drift.
- `scripts/generate_route_inventory.py --check`: FAIL — route inventory drift.
- Repository hygiene: FAIL — ten tracked root artifacts are outside the checker's allowlist.
- Some nominal “check” scripts regenerate dozens of tracked reports rather than operating read-only. Audit-generated changes had to be restored after execution.

### 7.4 Static quality

- Ruff: 443 findings across app/tests.
- Mypy: 378 errors in 100 files out of 458 checked.
- Black was referenced by `make lint` but absent from all dependency manifests. After installing current Black, 1,220 files would be reformatted and 143 left unchanged.
- Import Linter: 3 contracts kept, 0 broken. This is a narrow positive and does not offset the type and style debt.

### 7.5 Coverage

No fresh trustworthy coverage result was produced. The ignored `.coverage` file was dated 2026-07-02 and reports 0.0% across 31,043 measured statements, so it is unusable as a baseline. The repository threshold is 67%, but the current fast gates explicitly disable coverage.

The Makefile coverage target runs the test command with `|| true`, then relies on the final coverage report threshold to fail. This permits test failures to be obscured by a later aggregate result and should be replaced with explicit preservation of both test and threshold exit states.

## 8. Security and dependency posture

### 8.1 Dependency findings

Fresh audits on 2026-07-10 found:

- Base Python lock: **87 known vulnerabilities in 15 packages**.
- ML Python lock: **46 known vulnerabilities in 6 packages**.
- Frontend production lock: **1 high and 1 moderate vulnerability**; the high issue is in `ws@8.20.1`, fixed from 8.21.0.
- The CI command that audits base and ML locks together cannot resolve because base pins Jinja2 3.1.4 while ML pins 3.1.6.

Notable affected Python packages include Starlette, python-multipart, aiohttp, PyJWT, pypdf, azure-identity, Jinja2, urllib3, transformers, torch, and MCP. Counts include multiple advisories per package and must be triaged for reachability, but they are far beyond an acceptable unreviewed release baseline.

### 8.2 Static security findings

Bandit scanned approximately 69,333 lines and reported:

- 3 high-severity findings.
- 20 medium-severity findings.
- 64 low-severity findings.

High findings include Jinja2 `autoescape=False` in diagnostic item generation and two MD5 uses in ETL code. MD5 may be non-security deterministic hashing in one location, but it needs an explicit `usedforsecurity=False`/documented disposition rather than silent acceptance.

Medium findings include unpinned Hugging Face downloads with `trust_remote_code=True`, use of `eval` for expression scoring, dynamic SQL construction, and file-permission concerns.

### 8.3 Secret scanning

A source scan over `app`, `scripts`, and `.github` produced 879 candidate findings. The committed `.secrets.baseline` also contains 879 entries. This does not prove 879 real secrets; most may be fixtures, hashes, evidence, or false positives. It proves that the baseline is extremely noisy and has not been reduced to a reviewable release signal.

The full-repository scanner also showed poor operational behavior, spawning multiple CPU-saturating workers and not completing within the audit window. The scan was stopped and its automatic baseline rewrite was reverted.

### 8.4 Positive security controls

The following are real positives:

- Production config requires Azure Key Vault and fails closed without it.
- Production placeholder JWT secrets are rejected.
- The development session endpoint is gated out of production.
- Metrics are restricted to direct private client ranges in production.
- Request IDs, structured logs, audit tables, rate limiting, and security headers exist.
- Import boundaries prevent the POPIA router from constructing repositories directly.

These controls are valuable foundations, but several are verified only statically and do not erase the runtime/auth/schema/security failures.

## 9. CI/CD and evidence governance

The repository contains 86 workflow files. This provides broad automation coverage but also creates significant workflow sprawl and makes it difficult to know which checks are authoritative.

Key observations:

- `ci-core.yml` runs the same unit and integration gates that are currently red locally.
- `ci-cd.yml` marks mypy as `continue-on-error` and restricts blocking Ruff to a small critical-error subset, so hundreds of known errors are non-blocking by design.
- `ci-cd.yml` runs the combined pip-audit command that currently fails dependency resolution before it can audit.
- Schema CI validates the repository graph and ORM metadata but does not prove an existing live database is at the repository head.
- Many PRD/RR/KG workflows run one focused evidence test and a self-verifier. Passing those jobs can prove record consistency without proving application behavior.
- No authoritative current remote CI run was captured during this audit.

The evidence system has become capable of self-confirmation: a dataclass returns `accepted`, a test asserts `accepted`, a verifier checks that the test/file/string exists, and an evidence record stores `accepted`. That chain is internally consistent but not independent evidence.

## 10. Documentation truth assessment

### 10.1 Directionally accurate documents

`docs/project_status.md` and the June release go/no-go report remain directionally correct where they say the project is RED/NO-GO and block release, staging, legal/security sign-off, and live learner traffic.

### 10.2 Stale or contradicted claims

Examples:

- `docs/project_status.md` says OpenAPI, route inventory, frontend lint, type-check, and Vitest pass. Current results show OpenAPI drift, route drift, lint failure, and 3 Vitest failures. Only type-check remains green.
- `docs/current_state.md` was last reviewed on 2026-07-02 and describes PRD-0.1 as current, while the production register now claims PRD-9 closure and PRD-10 next.
- The production-readiness register says PRD-9 is closed and commercial runtime blockers are remediated, while the current readiness probe is 503, the live database lineage is unknown, integration/unit/frontend gates are red, and dependency audits are red.
- The runtime KG implementation/authority records may describe governance state, but the live database lacks the current runtime KG and curriculum tables.
- The PRD-9 record states repository hygiene is repaired, while its own current verifier reports hygiene false.

Documentation should therefore be treated as historical/governance input until regenerated from the evidence in this report.

## 11. Readiness scorecard

| Area | State | Evidence boundary |
|---|---|---|
| Source breadth | GREEN | Large backend/frontend/product surface exists. |
| Backend import/buildability | GREEN | Both FastAPI applications import. |
| Frontend production build | GREEN | Next build completes. |
| TypeScript | GREEN | `tsc --noEmit` passes. |
| Mocked browser journeys | GREEN | 4/4 targeted Chromium journeys pass. |
| Backend unit gate | RED | Stops at 20 failures. |
| Backend integration gate | RED | 2 failures; 247 skipped. |
| Frontend lint/tests | RED | 1 lint error; 3 Vitest timeouts. |
| OpenAPI/route artifacts | RED | Both drift checks fail. |
| Runtime stack | RED | `/ready` is 503; Redis/API/worker/frontend not live as a stack. |
| Database lineage/schema | CRITICAL RED | Unknown live revision; 54 ORM tables missing. |
| POPIA end-to-end behavior | RED | HTTP lifecycle failures and type mismatches. |
| Billing | RED | Placeholder email; no live provider proof. |
| Security dependencies | CRITICAL RED | 87 base, 46 ML, 2 frontend findings. |
| Static Python quality | RED | 443 Ruff and 378 mypy errors. |
| Coverage | UNKNOWN/RED | No fresh trustworthy baseline. |
| Remote CI | UNKNOWN | Not captured in this audit. |
| Staging/production | UNKNOWN/RED | No deployed proof; local readiness fails. |
| Release/public beta/live traffic | NO-GO | Explicitly unsafe and not proven. |

## 12. Prioritised remediation roadmap

### P0 — stop false closure and restore a trustworthy baseline

1. **Freeze PRD-10 handoff and release claims.** Mark the PRD-9.5-9.9 remediation record as contradicted/pending. Change the commercial remediation endpoint to derive state from actual probes or return a non-authoritative planning payload.
2. **Reconcile database lineage before any upgrade.** Snapshot the Supabase database; inventory its DDL; identify the source of revision `20260531_1600`; decide whether to create an explicit bridge migration or rebuild a disposable canonical database. Do not stamp or upgrade blindly.
3. **Make migration readiness exact.** Compare live revision(s) with Alembic repository head and fail if the live revision is unknown, split, behind, or ahead. Add required-table/column probes for critical runtime paths.
4. **Restore a complete disposable stack.** PostgreSQL, Redis, API, worker, and frontend must run together from committed configuration. Run migrations from base to head on a fresh database.
5. **Repair POPIA runtime wiring.** Align route request types, adapter return types, canonical service signatures, and auth fixtures. Require the two failing lifecycle tests to pass with no skips.
6. **Fix the actual fast gates.** Mark governance tests correctly or split them from product tests; repair stale state assertions; then obtain a complete unit result without orphaned xdist workers.
7. **Block on current dependency audits.** Recompile coherent base/dev/ML locks, remove the Jinja2 conflict, update high-risk dependencies, and make audit commands independently resolvable and release-blocking.
8. **Triage the secret baseline.** Review the 879 candidates, remove real secrets if any, suppress fixtures precisely, and reduce the baseline to a human-reviewable set.

### P1 — repair core product fidelity

9. **Fix learner-service dependency injection and UUID contracts.** Tests and implementation currently disagree on constructor ownership and accepted IDs.
10. **Replace placeholder object authorization.** Guardian/learner and teacher/learner relationship checks must use repositories and be covered through HTTP denial/allow tests.
11. **Repair frontend quality gates.** Fix conditional hooks, stabilize the three timed-out tests, remove `act(...)` warnings, and decide whether the 75 `any` warnings are acceptable debt or blockers.
12. **Regenerate OpenAPI and route inventory from the final code state.** Make checks read-only and fail on drift without rewriting unrelated tracked reports.
13. **Establish a real coverage baseline.** Run product unit and integration tests against a fresh migrated database, preserve test failure exit codes, and publish line/branch coverage by domain rather than one opaque aggregate.
14. **Resolve high-impact static security findings.** Remove unsafe template rendering, pin trusted model revisions, avoid `trust_remote_code` where possible, replace `eval`, parameterize dynamic SQL, and document non-security hashes explicitly.
15. **Finish billing runtime contracts.** Retrieve/decrypt the actual guardian billing email, align the audit service interface, and test idempotent checkout/webhook/subscription transitions against Stripe test mode.

### P2 — simplify governance and prove deployment

16. **Reduce workflow sprawl.** Define a small required-check set: backend product tests, integration/migrations, frontend quality/build, security/dependencies, contract drift, and E2E. Make PRD/RR evidence jobs informational unless they execute independent runtime proof.
17. **Separate implementation, governance, and evidence tests.** Evidence tests must not be able to declare their own success from constants or mutable records.
18. **Consolidate duplicate runtime families.** Reduce legacy/current auth, consent, data-rights, tutor, repository, route alias, and deployment surfaces.
19. **Deploy a clean staging environment.** Apply migrations from base, seed controlled data, run backend-backed learner/parent/diagnostic/privacy/billing journeys, and capture rollback evidence.
20. **Obtain external gates.** Independent security review, POPIA/legal review, content licensing, product approval, branch protection, backup/restore, and operations sign-off remain mandatory before real learner data.

## 13. Minimum release acceptance criteria

No release/public-beta decision should be reconsidered until all of the following are true on the same candidate commit:

- Clean worktree and traceable commit/branch provenance.
- Fresh database migrates from base to the exact repository head.
- Existing staging database revision is recognized and schema-drift check is clean.
- `/ready` returns 200 with all critical components healthy.
- Backend unit and integration gates complete with zero failures and no unjustified skips.
- Frontend type-check, lint, Vitest, production build, and backend-backed Chromium E2E all pass.
- OpenAPI and route inventories are current.
- Dependency audit has no unaccepted high/critical issues and all manifests resolve together.
- Secret baseline is reviewed and current.
- Coverage meets an agreed domain-based threshold with a fresh report.
- Billing test-mode flow, POPIA lifecycle, auth refresh/revocation, diagnostic flow, study plan, lesson completion, parent portal, and audit trail are verified end-to-end.
- Backup, restore, rollback, monitoring, alerts, and incident response are exercised in staging.
- Remote required checks and branch protection are captured.
- External security, privacy/legal, content, product, and operations approvals are explicit.

## 14. Final true-state statement

EduBoost V2 has substantial implemented foundations and can produce a successful frontend build and mocked user journeys. Its current source and live local infrastructure are not aligned. The project is carrying red product gates, schema-history divergence, missing runtime tables, stale generated contracts, dependency vulnerabilities, and governance records that can claim completion without independent runtime proof.

The current branch should not be used as evidence that commercial runtime blockers are remediated or that PRD-10 is ready to start. The next correct move is not more closure documentation; it is to re-establish one coherent executable baseline: a fresh canonical database, complete local stack, green product tests, exact readiness checks, and evidence generated from those results.
