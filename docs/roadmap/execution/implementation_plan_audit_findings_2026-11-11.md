---
title: "Implementation Plan - EduBoost V2 Audit Findings"
status: "in_progress"
owner: "engineering"
reviewers: [security-payments, privacy-legal, education-science, release-management]
audience: internal
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-11-23"
review_interval_days: 30
evidence_command: "See phase exit criteria in this plan"
code_anchors: []
---

# Implementation Plan: EduBoost V2 Audit Findings

## 1. Purpose and boundaries

This plan converts the September 23 True Status Report and the subsequent audit review into ordered, reviewable work. It keeps the historical report baseline distinct from later observations and uncommitted fixes.

The report baseline is commit ff0e09bc7c96e1effad822a45448e4b8a99e8c55. The current checkout is still at that SHA but contains uncommitted route-inventory, frontend build-URL, Compose, CI, deployment-helper, and known-issues changes. Treat those as proposals until separated, verified, and committed. Leave the pre-existing .agent.md edit and untracked September report outside remediation commits.

The report's 915 route count is historical. The explanation that it came from duplicate expansion is an inference until the unfixed generator is run under the exact environment that produced it. A source check, synthetic test, local image, or deployment manifest does not prove a live learner service.

Nothing in this plan authorizes production deployment, real payments, learner-data egress, learner recruitment, live LEV ingestion, or public beta traffic.

## 1.1 Implementation status (2026-11-23)

This plan is being implemented in the working tree. Completed changes are not release authorization and have not been applied to a deployed target.

| Finding / work item | Implementation evidence | State |
| --- | --- | --- |
| Generated-content containment | The quarantine script preserved byte-exact snapshots and hashes, then downgraded 41,911 generated approval labels across 204 generated artifacts. A follow-up found 14 synthetic approvals plus one reviewer-less human_reviewed row in the legacy 121-row CAPS bank; all 15 are now downgraded too. Current manifest covers 205 files and 41,926 downgraded records. | Applied to checkout; not verified in deployment databases |
| Generator self-approval | Item, lesson, and blueprint generators now emit ai_generated; the legacy scorer/generator no longer self-approves; item and lesson seeders require the independent review register for approved records; seeding rejects known synthetic or reviewer-less approval metadata; review service rejects the known synthetic UUIDs. Regression tests assert this. | Implemented; tests pass |
| Learner diagnostic/mastery shutdown | Default-off config gates return a stable 403 feature_disabled from canonical diagnostic, practice, assessment, onboarding, mastery, parent-summary, vertical-journey, and learner-item routes. | Implemented; canonical ASGI tests pass |
| User-facing state | Learner dashboard no longer fetches/renders mastery or diagnostic results; check-in page explains the pause. Parent dashboard and residual seeded report/diagnostic URLs no longer render IRT, archetype, gap, placement, or generated progress-summary values; mastery fixtures were removed from serialized server props. Added frontend acceptance coverage for the disabled screens. | Implemented; TypeScript check passes |
| Study plans | Route payload no longer includes runtime knowledge-graph mastery; service does not query mastery and the generated launch template is not loaded. | Implemented; unit test passes |
| Seed and legacy serving | Startup seed remains off unless the diagnostic feature is explicitly enabled; learner-item reads return empty while disabled. Existing production rows require the database migration below. | Partially implemented |
| Existing database approvals | Reversible migration 20261123_1200 downgrades generated/synthetic-approved item and lesson rows, including both known synthetic reviewer UUIDs and reviewer-less human_reviewed rows, while preserving prior review state. | Code added; not run against a disposable or deployed database |
| Deployment flag gate | The feature-flag checker is wired into PR Core and rejects enabled deployment flags without pilot authorization. | Implemented; static check passes |
| Wrong-key exposure investigation | The aggregate exposure query reports lower-bound counts. The incident record names the project owner as interim coordinator and keeps every target unknown. | Query implemented; no target DB/log access, so no exposure conclusion |
| Prospectus / learner guidance | Prospectus and learner guide no longer say the bank is approved or that mastery/check-ins are active. Updated prospectus PDF rendered and visually inspected. | Updated |
| Reviewer / curriculum release | No independent reviewer is named; no self-approval or learner release is permitted. Full CAPS/2026 ATP map and the signed Term 1 objective/item slice remain outstanding. | Blocked on external reviewer and curriculum work |

The generated-data labels changed in the checkout only. Database migration execution, environment-by-environment exposure review, image/target smoke runs, production readiness, and educator sign-off are still required. An unverified target is not a pass.

## 2. Governance and decisions

The proposed 9 November reviewer deadline has passed. Set a new date only after reviewer availability is confirmed.

Before any critical security row is classified green:

- The project owner sources an external security/payments reviewer who did not author the control.
- The project owner sources POPIA counsel for the legal questions in Section 5. Counsel, not the technical reviewer, decides legal interpretation.
- The project owner confirms the intended learner-serving deployment. Repository documentation names ACA as the production API target, but no frontend deployment resource or pipeline is present.
- Reviewers approve the sink-to-guard requirements, data categories, criticality, degraded behavior, and evidence rules before sink testing.
- Critical rows remain red if independent review is unavailable. Exceptions require owner, rationale, compensating control, approval, and expiry; expired exceptions fail CI.

Non-policy-dependent work may proceed while reviewers are sourced. Do not claim a reviewer has been contacted until outreach actually occurs.

## 3. Evidence and completion rules

Label each claim: pinned-image verified, disposable-runtime verified, ASGI/worker verified, source-only, inferred, unverified, or exception-approved. A helper-only unit test is not enforcement evidence.

For every sink, enter through the production ASGI app, worker runner, or CLI. Enumerate live routes and resolved dependencies; inspect the real middleware stack. Classify tests built with minimal FastAPI() apps as router-level/minimal-app evidence. Inspect conftest and fixtures for dependency_overrides that bypass authorization or billing.

Mutation tests must install a spy and prove the permissive stand-in ran. Mutate each defense-in-depth guard separately. Under mutation, the denied-path assertion must fail and the allowed-path assertion must still pass. A critical row is green only with a passing sink-level test in the audited runtime or an owned, approved, unexpired exception. Missing infrastructure means red/unverified.

## 4. Work phases

### Phase 0 - Freeze evidence and restart reviewer clock

**Priority:** P0. **Dependency:** none.

1. Preserve the pinned SHA and immutable image digest as baseline evidence. Record the current worktree diff without staging .agent.md or the untracked report.
2. Split existing uncommitted changes into isolated worktrees or commits, each referencing a finding. Keep baseline facts separate from fixes.
3. Prepare the brief in Section 5; source an independent security/payments reviewer and POPIA counsel; record names, scope, independence/conflicts, decision date, and evidence pointer.
4. Set a replacement review deadline after the reviewers accept.
5. Keep the 915 explanation marked inferred until Phase 1 reproduces it.

**Exit:** baseline cannot be confused with fixes; changes are isolated; reviewer roles are named or critical rows remain red.

### Phase 1 - Reproduce route and frontend build evidence

**Priority:** P0, parallel with Phase 0.

1. Create a clean worktree at the pinned SHA. Run the unfixed generator from that SHA using the repository virtual environment; record Python/FastAPI versions, command, and output. Compare against the pinned production image. Do not call the modified generator a reproduction.
2. If the unfixed local generator returns 915, state the dependency-drift cause only as reproduced. Otherwise trace the original environment and leave the cause unresolved.
3. Run the fixed generator under the canonical pinned dependency set in CI and locally. Require the same generated inventory and document the distinct meanings of application entries, inventory records, OpenAPI paths, and operations.
4. Build the frontend image with a unique sentinel API URL. Search the standalone server and browser bundles for the sentinel; search the entire build output for onrender.com. Confirm the committed .env.production no longer contains an API host.
5. Confirm whether a frontend resource exists in any deployment target. If not, mark deployed frontend as unverified. Treat ACA as intended only after owner confirmation, then feed its actual apiUrl output to the frontend build.

**Exit:** 915 is reproduced or remains explicitly unresolved; route checks are dependency-pinned; sentinel appears in the bundle and the stale Render host does not; intended frontend hosting is named or unverified.

### Phase 2 - Backend image containment and provenance

**Priority:** P0 before publishing images.

1. Replace broad backend COPY behavior with explicit backend-only paths; exclude app/frontend from API and worker images.
2. Replace the Docker ignore blocklist with a reviewed allowlist. Exclude .git, frontend dependencies/build output, local env files, docs/evidence, unapproved generated data, and developer artifacts.
3. Build deployable images in CI from a clean Git archive/worktree at the exact commit. Record source SHA, image digest, build-context manifest, SBOM, and provenance.
4. Inspect image filesystem/history. Verify no frontend source, node_modules, .next, env/secret files, docs, or unapproved content is present.
5. Investigate the retained 3.51 GB image: its app layer contains about 1.1 GB of frontend node_modules/.next. Search CI logs, deployment manifests, and registries to determine whether the image was pushed. If publication cannot be disproved, mark exposure unverified and handle it as potentially published. The earlier 708 MB measurement is not reproducible from retained images.
6. Replace copy-then-recursive-chown of the dependency tree with COPY --chown after validating ownership requirements.

**Exit:** clean archive image passes content policy, provenance is immutable, and the old image's publication status is documented.

### Phase 3 - Commit the disposable stack and sink tripwire

**Priority:** P0. **Dependencies:** pinned image and reviewed sink requirements.

Commit a disposable harness that starts an isolated network with PostgreSQL/pgvector, Redis, the API image, and worker runner; applies migrations; runs smoke/integration paths; and reliably removes resources. Use fake provider credentials, no developer data or volumes, and no production services.

The harness must:

- Patch low-level Stripe and provider SDK/HTTP clients with recording fakes that execute normal wrappers and capture call stacks.
- Instrument learner repository writes/deletes and add SQL/ORM instrumentation where the repository layer is not a choke point.
- Exercise integration tests, ARQ jobs, scripts, CLI commands, and all served FastAPI apps. First determine whether api_v2_routers/api_v2.py is served; remove it or document its entrypoint.
- Generate route drivers from live OpenAPI and exercise sink-reaching routes unauthenticated and under a wrong role using safe fake data.
- Inspect every FastAPI() test app and dependency override; label minimal-app tests and disqualify them as production-app enforcement evidence.
- Diff observed runtime sinks against the inventory; an unlisted observed caller is a finding.
- Validate mutation spies and positive/negative assertions for each guard.

**Exit:** a clean checkout can reproduce the stack; tests run inside the built image; every observed caller is accounted for and evidence identifies the entrypoint/dependencies.

### Phase 4 - Enforce critical sinks

**Priority:** P0. **Dependencies:** signed requirements and Phase 3 harness.

Implement and verify in this order: outbound Stripe, LLM calls, learner deletion, then inbound webhook. Also cover the additional sinks below.

- **Outbound Stripe:** guardian authentication; billing authorization; deterministic idempotency from guardian, plan, and a user-intent ID minted once; bounded retry window; server uniqueness for open checkout; test/live key-mode lock.
- **LLM calls:** budget reservation before every provider call; safety screening; classify data before egress; apply redaction and consent rules only for learner data. Curriculum-only embeddings with no learner data require budget enforcement, not learner-consent coverage. Generate the path-to-mechanism map from tripwire observations and obtain reviewer approval.
- **Learner deletion:** ownership and role checks, audit proof, harmless repeat execution, retained-row scan for raw/relinkable IDs, and reviewer decision on keyed proof versus raw ID. Counsel decides whether soft delete satisfies erasure policy.
- **Stripe webhook:** raw-body signature with timestamp tolerance, persisted event-ID deduplication, idempotent handler, fail-closed missing secret. Do not register a live endpoint until payments are authorized; test sandbox retry behavior.
- **Other sinks:** data export, guardian email/SMS, learner writes, cross-learner reads, mastery serialization, content-factory promotion, LEV ingestion, and rate limiting. Enforce at server-side sink; frontend guards are UX only.

Test allowed/denied, unauthenticated, wrong-role, replay/retry, and infrastructure-failure paths as applicable. Minimal-app tests do not close findings.

**Exit:** inventory covers every tripwire-observed caller; approved controls run at each sink; mutations fail denied-path tests; no critical row is green from source presence alone.

### Phase 5 - Redis accounting and probes

**Priority:** P0. **Dependency:** reviewer approval of budget semantics.

1. Adopt the proposed policy: outage-period generation usage counts toward the cap and is reconciled when Redis recovers.
2. Do not rely on a process-local counter for strict enforcement: it is per process, diverges across replicas, and disappears on process exit. Use an idempotent durable usage ledger/outbox or reviewed authoritative store, keyed by stable request ID. Test retry, partial flush, process restart, and multi-replica behavior.
3. Add a rate-limiter requirement row. Decide/test behavior during Redis loss per path, including cross-replica limits.
4. Add a liveness probe independent of Postgres/Redis.
5. Liveness alone does not stop a readiness probe from withdrawing every replica from ingress. Do not keep Redis-critical /ready as ACA traffic readiness if tutoring must remain available. Use core/capability runtime readiness for ACA and retain a strict deployment gate that checks Redis/content before rollout. Have the release pipeline call the strict gate; test the actual platform probe behavior.
6. Verify ACA, Render, Compose, and worker probes.

**Exit:** outage usage survives process/replica changes, rate-limiter degradation is explicit, Redis loss does not restart instances or black-hole DB-backed tutoring, and deployment gates remain strict.

### Phase 6 - Approved content and pgvector readiness

**Priority:** P1 before learner-facing launch.

1. Choose the study-plan template source: an allowlisted, approval-marked, SHA-256-pinned artifact or a versioned database record. Do not copy all data/generated into the image.
2. Replace silent production fallback with degraded readiness/capability status when required personalization content is absent or invalid.
3. Establish production content provisioning as an explicit one-off seed/publication job; keep opportunistic startup seeding disabled unless reviewed deployment config enables it.
4. Add readiness/release checks for approved Grade 4 diagnostic items and lessons. Use the approved launch scope and versioned policy thresholds, not an unreviewed hard-coded total. Return counts without learner data.
5. Test empty, below-threshold, and sufficient content in disposable Postgres.
6. For Azure PostgreSQL Flexible Server, allowlist extension name vector, create it in each database, and verify the actual migration identity. Determine whether the extension is trusted under the target service/version: Microsoft documents that trusted extensions require database CREATE privilege while untrusted extensions require azure_pg_admin. If elevated extension setup is needed, use a controlled bootstrap identity and keep application migrations least-privileged.
7. Treat live DB content and extension state as unverified until checked through authorized access.

**Exit:** required template is approved/hash-checked or DB-backed; readiness proves approved content; seed and extension setup are reproducible and least-privileged.

### Phase 7 - LEV consent, integrity, and evaluation boundary

**Priority:** P0 before real LEV ingestion; empirical evaluation waits for learner-data/recruitment authority.

1. Make omitted consent invalid. Check authoritative consent at ingestion and fail closed for unknown, withdrawn, expired, or non-consented states.
2. Add runtime API/worker ingestion only after reviewer and counsel approve data category, lawful basis, egress, retention, and access controls.
3. Enforce append-only storage with database permissions/triggers or an immutable store. Specify canonicalization, key custody, chained integrity, verification, retention, deletion, and tamper evidence.
4. Test unauthorized ingestion, missing/withdrawn consent, tampering, update/delete attempts, retention, and pseudonym linkage.
5. Keep synthetic fixtures labelled synthetic. Do not claim empirical calibration, fairness, or impact until an independent education-science protocol runs on authorized data.
6. Counsel answers the POPIA questions in Section 5; technical review cannot substitute for legal advice.

**Exit:** no consent fail-open; database-level integrity withstands mutation tests; external approvals and evidence pointers exist; real-cohort evaluation remains blocked until authority is granted.

### Phase 8 - Restore CI gates and publish a current report

**Priority:** P1 after fixes stabilize.

1. Resolve the 18 content-factory failures against the canonical response-envelope contract and the remaining provider test.
2. Fix the four report-time Mypy errors; rerun the exact PR-core target in pinned local/CI dependencies.
3. Install the frontend lockfile in frozen mode at declared versions; run lint, type-check, unit tests, and production build. Replace Playwright dry-run and swallowed errors with real learner/parent journeys against the disposable stack.
4. Triage async mock warnings, short test HMAC keys, and other actionable warnings.
5. Produce measured coverage at the configured threshold; static threshold alignment is not measured coverage.
6. Run OpenAPI/inventory checks in the same pinned dependency environment.
7. Gate CI on database migration upgrade/downgrade, pgvector integration, Redis outage/recovery, sink tests, image contents, and frontend sentinel verification.
8. Query hosted CI and deployment evidence for the target commit. Do not claim a live learner service without current endpoint and telemetry evidence.
9. Publish a new current-state report with commit and immutable image digest. Keep the September report historical; distinguish baseline results from fixes.

**Exit:** required CI passes without swallowed errors; measured coverage and runtime evidence exist; all unverified critical items remain red or have approved active exceptions; report claims match captured evidence.

## 5. One-page reviewer brief

Criticality below is proposed and requires sign-off. Security/payments reviewer approves technical controls. POPIA counsel approves legal interpretation.

| Sink | Proposed criticality | Required guard/evidence |
| --- | --- | --- |
| Outbound Stripe | Critical: money | Authenticated guardian; billing authorization; stable per-intent idempotency; server uniqueness; retry horizon; key-mode lock; mutation-tested ASGI path. |
| Stripe webhook | Critical: money/state | Raw-body signature and timestamp tolerance; persisted event dedupe; idempotent handler; missing-secret fail-closed; live endpoint withheld until authorized. |
| LLM with learner data | Critical: child data/safety | Budget; safety; category-specific redaction; consent/legal decision before egress; runtime provider tripwire. |
| Curriculum-only embedding | High: spend/content | Budget; prove no learner data in request. |
| Learner writes/deletion | Critical: child data | Server ownership/role; audit record; repeat-safe erasure; retained-identifier/linkage review; repository/ASGI mutation tests. |
| Data-subject export | Critical: child data | Requester and ownership check; scoped output; audit; no cross-learner data. |
| Cross-learner reads | Critical: child data | Server ownership or verified assignment; wrong-role/wrong-learner denied before output. |
| Mastery serialization | Critical: learner claims | Server auth/ownership; confidence ceiling; serialized output tested through ASGI. |
| Guardian email/SMS | High: family contact | Verified recipient; consent/preferences; recipient ownership; rate limit; send provider captured. |
| Content promotion | High: learner safety | Approved reviewer state; content hash/provenance; safety/curriculum review; promotion authorization. |
| LEV event ingest | Critical before real data | Explicit consent; minimization/pseudonym policy; authorization; append-only persistence; integrity and retention. |
| Redis rate limit | High: abuse/availability | Route-specific outage policy; multi-replica test; no claim that process-local counters are global. |

### Questions for POPIA counsel

- What rules apply to children's personal information for each purpose and data category?
- Does section 72 apply to each provider egress/hosting path, and what transfer safeguards/contracts are required?
- What consent proof, guardian authority, withdrawal, retention, deletion, and audit evidence are required?
- Does soft delete plus pseudonymized audit evidence satisfy the intended erasure policy? Which retained identifiers must be removed or keyed-hashed?
- Which LLM, email, SMS, analytics, and hosting providers may receive each data category and in which jurisdictions?

Record reviewer identity, independence/conflicts, scope, decision, date, conditions, and evidence pointer. Until then, critical rows remain red or under an approved expiry-bound exception.

## 6. Cross-phase release gate

A release candidate is not ready until independent requirements review is recorded; runtime tripwires account for every observed sink; denied/allowed and mutation tests pass; no expired exception exists; clean API/frontend images have immutable provenance; the actual frontend target is verified; readiness proves approved database content and required services; pgvector and migrations work under the intended role; Redis accounting and probe behavior pass outage/recovery tests; backend, frontend, type, coverage, migration, integration, and real Playwright jobs pass; and production, learner-data, payment, or empirical LEV claims have separate authorization and evidence.

## 7. Technical references

- Microsoft Learn, allow extensions: https://learn.microsoft.com/en-us/azure/postgresql/extensions/how-to-allow-extensions
- Microsoft Learn, extension creation and roles: https://learn.microsoft.com/en-us/azure/postgresql/extensions/how-to-create-extensions
- Microsoft Learn, pgvector and extension name vector: https://learn.microsoft.com/en-us/azure/postgresql/extensions/how-to-use-pgvector
