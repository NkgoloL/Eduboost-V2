# EduBoost V2 North Star TODO - 2026-05-22

Audit snapshot for branch `codex/production_readiness` at commit `db14a6821eb14de532434360265a7370119b04ac`.

## Executive Status

EduBoost is moving in the correct direction. The highest-risk backend boot blockers from the last push have been reduced: production no longer hard-requires Azure Key Vault, Postgres URL handling supports async SQLAlchemy on Render/Supabase, the Supabase schema has been migrated, `irt_items` has been seeded, `/api/v2/health/deep` has passed against staging, and the staging smoke workflow has a successful GitHub Actions run.

The project is still not beta-ready. The remaining work is less about one broken table and more about closing evidence, frontend runtime proof, external approvals, transaction guarantees, and production operations. The current release status files still say `NO-GO`, and some of them are stale relative to HEAD.

## Current Truth

### Backend and Database

- No ORM-declared runtime table is currently missing from live Supabase. The live database includes the runtime tables expected by the application metadata, including `audit_events`, `audit_logs`, `calibration_audits`, `diagnostic_items`, `diagnostic_sessions`, `guardians`, `irt_items`, `item_exposures`, `knowledge_gaps`, `learner_profiles`, `lesson_feedback`, `lessons`, `mastery_snapshots`, `parental_consents`, `practice_queue`, `rlhf_exports`, `spaced_review_schedule`, `stripe_webhook_events`, `subject_mastery`, and `topic_mastery`.
- Live Supabase also contains extra public tables not declared in current ORM metadata: `consent_records`, `data_export_requests`, `erasure_requests`, `correction_requests`, and `restriction_requests`. These are likely POPIA/DSR persistence tables and need an ownership decision: add ORM models, document them as SQL-only tables, or retire/merge them.
- `alembic_version` is present and reports revision `20260516_0100`.
- `irt_items` is populated with 1600 rows.
- `diagnostic_items` exists but has 0 rows. This may be acceptable if diagnostics are fully backed by `irt_items`; otherwise it is a functional data gap.
- `audit_events` exists but had 0 rows at audit time. This is acceptable only if no audited staging flow has run yet; otherwise audit-write proof is missing.

### Evidence and Release Gates

- Staging smoke evidence has been accepted with GitHub Actions run `26247145077`.
- Deep health runtime evidence has been accepted with GitHub Actions run `26257276487`.
- `docs/release/final_beta_gate_refresh.json` still reports `NO-GO`, 8 beta blockers, and a stale commit `ecaab870ed5e171a5d8c5d58393ae80e64917ee5`.
- `docs/release/release_go_no_go_status.json` still reports `NO-GO`, 9 beta blockers, and a very stale commit `84ace987e1f577fcf647fbe105f78680003c5aaa`.
- Several evidence files and registry entries are now inconsistent: some items are runtime-passing but still beta-blocking because their closure blockers require live external proof.

### Frontend

- Frontend dependency install was stale at audit start: `node_modules` existed but `tsc` and `vitest` binaries were missing. Running `npm ci` repaired the local dependency install without tracked file changes.
- Frontend unit tests pass: `npm run test` completed with 20 test files and 85 tests passing.
- Frontend type-check fails: `npm run type-check` includes root `__tests__` files but does not configure Vitest globals/types, causing missing `test`, `expect`, `beforeEach`, `afterEach`, and `describe` symbols. `__tests__/ErrorBoundary.test.tsx` also has invalid JSX test helper components that return `void`.
- Frontend build fails locally because `.next` is root-owned and `next build` cannot write `.next/trace`. This is a workspace artifact, but it blocks local build proof until the generated cache is removed or ownership is repaired.
- `npm ci` reports 11 vulnerabilities, including 4 high severity vulnerabilities, plus deprecated packages such as `@supabase/auth-helpers-nextjs` and ESLint 8.
- The production readiness contract still lists P0 flows whose repository evidence is documentation-only rather than implemented/runtime-proven: password reset request, password reset completion, email verification, onboarding completion, privacy controls, WCAG/mobile proof, and parts of parent/learner runtime evidence.
- Frontend deployment proof is still incomplete: `DEPLOY-FE-001` and `DEPLOY-FE-RUNTIME-001` remain config/local-preflight style evidence until a real staging deployment and browser smoke run are attached.

## North Star TODO

### P0 - Beta Gate Blockers

- [ ] Refresh the release gate truth from current HEAD. Run the final gate/status generators, reconcile stale commit SHAs, and ensure `release_go_no_go_status`, `final_beta_gate_refresh`, CI evidence, external approval status, staging acceptance, and blocker burndown all agree.
- [ ] Attach authoritative current CI evidence. Add a passing GitHub Actions run URL, commit SHA, workflow name, result, verifier, and verification date for the release branch.
- [ ] Close external approval gates. Attach Legal/POPIA, Security, Curriculum/Content, and staging acceptance approval metadata with evidence URLs and named approvers.
- [ ] Close `JWT-001`. Provide production/staging secret provisioning evidence, fallback-disabled proof, rotation notes, and verifier metadata.
- [ ] Close `ARQ-001`. Run a live Redis worker enqueue/dequeue proof against staging, attach logs/run URL, and verify worker import/startup in the target environment.
- [ ] Close `LESSON-AUTH-001`. Run full HTTP staging authorization proof for all lesson routes, including negative access checks.
- [ ] Close `DIAG-SCORE-001`. Run live DB diagnostic scoring proof, including historical response scoring, score snapshot creation, and audit trail verification.
- [ ] Close frontend runtime proof. Deploy the frontend to staging, configure `NEXT_PUBLIC_API_URL` to the real API root, run browser smoke/E2E tests for auth, learner, diagnostic, lesson, parent, and privacy flows, and attach evidence.

### P0 - Database and Data

- [ ] Make migrations repeatable from a clean database. Convert the successful Supabase migration path into a documented command or CI/manual job that can recreate schema and seeds without one-off SQL cleanup.
- [ ] Decide ownership for live-only POPIA/DSR tables: `consent_records`, `data_export_requests`, `erasure_requests`, `correction_requests`, and `restriction_requests`. Add ORM models/tests or document them as SQL-owned tables with repository evidence.
- [ ] Decide whether `diagnostic_items` should be populated. If yes, seed it and add verification counts. If no, document that `irt_items` is canonical and update health/evidence expectations accordingly.
- [ ] Add explicit audit write proof. Exercise a staging flow that writes to `audit_events`, then verify the row and attach evidence.
- [ ] Add migration rollback/restore evidence. Prove backup, restore, and rollback posture for Supabase/staging before beta data collection.

### P0 - Frontend Readiness

- [ ] Fix frontend type-check. Add Vitest globals/types or test-specific TypeScript config, and fix invalid JSX test helper components.
- [ ] Fix local build proof. Remove or repair the root-owned `.next` cache and rerun `npm run build` under Node 20.
- [ ] Triage frontend dependency risk. Address 11 `npm audit` findings, prioritize the 4 high severity issues, and replace deprecated `@supabase/auth-helpers-nextjs` with the current Supabase SSR/client pattern.
- [ ] Implement password reset request and completion screens with tests.
- [ ] Implement email verification UX with tests.
- [ ] Implement onboarding completion route/state with tests.
- [ ] Implement runtime privacy controls for export, erasure, correction, and restriction requests, then prove them against staging.
- [ ] Add browser E2E coverage for guardian signup/login/logout/session expiry, learner dashboard, diagnostic flow, lesson flow, parent dashboard, and privacy requests.
- [ ] Add mobile and accessibility proof: responsive viewport checks, keyboard navigation, landmark/label checks, contrast review, and screen-reader state review.
- [ ] Prove frontend environment safety. Validate no server secrets are exposed through `NEXT_PUBLIC_*`, and prove production disables `NEXT_PUBLIC_ENABLE_DEV_SESSION`.

### P1 - Production-Ready Engineering

- [ ] Close transaction proof items: `TX-001`, `TX-POPIA-001`, `TX-AUTH-001`, `TX-DIAG-001`, `TX-LESSON-001`, `TX-ROUTE-001`, and related route transaction rollups.
- [ ] Close live route rollback evidence for auth, POPIA, diagnostics, and lesson routes.
- [ ] Complete `AUTH-REPO-001`: live Postgres repository proof, Redis token cache proof, and full staging auth flow proof.
- [ ] Complete `AUTH-SERVICE-CLEANUP-001`: make auth router logout/revoke-all paths delegate consistently to `auth_service`.
- [ ] Reduce router repository/import debt from `ARCH-001R` and shrink any import-linter ignore surface.
- [ ] Add OpenAPI drift enforcement to CI and attach evidence.
- [ ] Add production observability evidence: Sentry/structured logs, health alerts, Redis/Postgres checks, and incident runbooks.
- [ ] Add rate-limit, abuse, and payment webhook replay evidence for staging.
- [ ] Add data retention and deletion operational runbooks aligned with POPIA approvals.

### P2 - Scope Decisions

- [ ] Decide whether teacher dashboard and admin console stay explicitly gated for beta or move into implementation scope.
- [ ] Decide PWA/offline beta scope. If included, prove service worker registration, cache behavior, offline messaging, and low-data mode. If deferred, keep it explicitly out of beta acceptance.
- [ ] Decide whether frontend and backend deploy independently or as a single release train, then reflect that in release docs and CI gates.

## Implementation Roadmap

### Phase 0 - Stabilize the Audit Baseline, 0.5 to 1 day

1. Run current gate refresh commands from HEAD and commit only generated status updates that are intentionally current.
2. Run backend release checks and collect fresh pass/fail output.
3. Run frontend `npm ci`, `npm run test`, `npm run type-check`, and `npm run build` under Node 20.
4. Query live Supabase table inventory and key counts again; save the output as evidence.
5. Update this TODO if any blocker count changes.

Acceptance: one current audit pack exists, status files reference HEAD, and known blockers are not stale artifacts.

### Phase 1 - Close Evidence Before More Feature Work, 1 to 2 days

1. Attach authoritative CI run metadata.
2. Attach external approval metadata for Legal/POPIA, Security, Curriculum/Content, and staging acceptance.
3. Run live JWT guard proof and ARQ Redis worker proof.
4. Rerun `make final-gate-refresh` and verify blocker count drops for real.

Acceptance: release gate files agree on blocker count and no accepted item still looks externally blocked because metadata is missing.

### Phase 2 - Make Database Proof Repeatable, 1 to 2 days

1. Convert the Supabase migration and seed path into a clean repeatable command/script.
2. Decide and document ORM ownership for POPIA/DSR tables.
3. Resolve `diagnostic_items` row-count ambiguity.
4. Add audit-event write proof and backup/restore proof.

Acceptance: a clean staging database can be created, migrated, seeded, health-checked, and evidenced without manual SQL surgery.

### Phase 3 - Frontend Production Readiness, 2 to 4 days

1. Fix TypeScript test globals/config and invalid test helpers.
2. Fix local build proof and dependency audit findings.
3. Implement missing P0 UX flows: reset, verification, onboarding completion, and privacy controls.
4. Add browser E2E smoke against the real staging API.
5. Deploy frontend staging and attach browser proof.

Acceptance: frontend has passing tests, type-check, build, env check, accessibility/mobile checks, and staging browser smoke evidence.

### Phase 4 - Live Route and Transaction Proof, 2 to 3 days

1. Prove lesson authorization through staging HTTP tests.
2. Prove diagnostic scoring through live DB and audit checks.
3. Prove route transaction rollback behavior across auth, POPIA, diagnostics, and lessons.
4. Complete auth repository/service cleanup evidence.

Acceptance: route-level production behavior is proven with live DB evidence and rollback/audit checks.

### Phase 5 - Final Gate, 0.5 to 1 day

1. Regenerate all release status files from HEAD.
2. Run final gate and beta gate checks.
3. Attach the final evidence URLs and approver metadata.
4. Cut the final GO/NO-GO decision.

Acceptance: `release_go_no_go_status` and `final_beta_gate_refresh` agree on GO, or the remaining NO-GO blockers are explicit external business decisions rather than hidden engineering unknowns.
