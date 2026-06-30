# EduBoost V2 Production Readiness Roadmap

Date: 2026-05-11

This roadmap explains how to tackle `TODO.md` in the correct order. It is an
execution guide, not a replacement for the TODO list. `TODO.md` remains the
granular backlog; `docs/current_state.md` remains the current-state source of
truth.

## Operating Rules

1. Do not mark a TODO item `[x]` until it has both implementation evidence and
   verified green evidence.
2. Use `[verify]` when code, scripts, workflows, or docs exist but the exact
   item has not been proven by a named command, CI run, staging run, or release
   evidence artifact.
3. Keep high-level rollup items `[verify]` while any granular backlog beneath
   them remains open.
4. Each work batch must end with a small evidence bundle: changed files,
   commands run, test output summary, and any remaining verification gap.
5. Prefer closing release blockers before expanding product scope.

## Definition Of Done

An item may be marked `[x]` only when all of the following are true:

- The source, test, workflow, migration, runbook, or legal artifact exists.
- The item is covered by a focused test, script, CI job, staging validation, or
  manual review record appropriate to the risk.
- The passing command or evidence artifact is named beside the TODO item.
- The claim does not depend on unchecked granular subitems.

## Execution Gates

### Gate 0: Stabilize Truth And Provenance

Goal: make the repo, branch, release authority, and documentation rules
unambiguous before claiming readiness elsewhere.

TODO sections:

- `0. Repository state and canonical source of truth`
- `17. Documentation, ADRs, and claim discipline`

Exit evidence:

- `docs/repository_governance.md` confirms canonical repo, branch, fork policy,
  release authority, and hotfix authority.
- `scripts/verify_repo_state.py` and `make verify-repo-state` exist.
- Repo-state verification records head SHA, branch, remote, dirty-state policy,
  and accepted freshness marker.
- `docs/current_state.md` links only to current verified evidence.

### Gate 1: Runtime And API Contract Baseline

Goal: make the backend runtime deterministic and contract-checkable.

TODO sections:

- `1. PR-002R replacement - backend runtime and API contract baseline`
- Relevant backend checks in `14. Testing, release evidence, and quality gates`

Exit evidence:

- `app.api_v2:app` imports cleanly.
- Router registration is fixed and covered by regression tests.
- Legacy route exposure is explicitly blocked or documented.
- API response and error envelopes are standardized.
- OpenAPI generation and drift checks are green.
- `make runtime-check`, `make openapi-check`, route inventory checks, and
  focused PR-002R tests pass.

### Gate 2: Security, Auth, Consent, And POPIA Boundary

Goal: prove real learner data cannot be accessed, processed, exported, or
erased outside the intended authorization and consent boundaries.

TODO sections:

- `3. Authentication, sessions, RBAC, and object-level authorization`
- `4. POPIA consent, privacy, data-subject rights, and audit`
- `15. Security posture and threat modeling`

Exit evidence:

- Auth, token, cookie, RBAC, and object-authorization tests pass.
- Consent gates have positive and negative-path tests.
- POPIA export, erasure, correction, restriction, audit, and retention paths are
  covered by tests or documented manual review records.
- Security headers, CORS, CSRF posture, secrets policy, and threat model are
  documented with accepted risks.

### Gate 3: Data, Migrations, Backup, And Recoverability

Goal: prove the platform can be installed, migrated, backed up, restored, and
operated without hidden data-loss assumptions.

TODO sections:

- `5. Database, persistence, migrations, and performance`
- `13. Backup, restore, and disaster recovery`

Exit evidence:

- Migrations pass from an empty database and from the current expected baseline.
- Schema integrity validation passes.
- Repository and transaction boundary tests pass for critical data flows.
- Backup scripts, restore scripts, restore approval guard, and integrity checks
  are verified in a disposable environment.
- RPO/RTO and Redis recoverability assumptions are documented.

### Gate 4: AI, CAPS, Diagnostics, And Learning Model Proof

Goal: separate AI scaffolding from approved educational claims, then verify the
minimum learning loop for the launch scope.

TODO sections:

- `6. AI, LLM safety, lesson generation, and CAPS validation`
- `7. Diagnostics, assessment, item bank, and mastery model`

Exit evidence:

- LLM PII redaction, structured output validation, refusal behavior, provider
  fallback, and prompt fixture tests pass.
- CAPS claims are limited to reviewed evidence.
- Diagnostic item schema, IRT validation, item selection, item bank workflow,
  calibration, exposure limits, and session lifecycle are reconciled item by
  item against tests.
- Minimum launch item bank is approved for the claimed grade/subject scope.
- Mastery, progress, learning velocity, and remediation claims are backed by
  focused tests and do not exceed available item-bank evidence.

### Gate 5: Frontend, Journeys, Accessibility, And Low-Data UX

Goal: prove that learner and guardian workflows operate end to end through the
frontend, not only through backend contracts.

TODO sections:

- `8. Frontend production readiness and UX`
- Frontend and E2E checks in `14. Testing, release evidence, and quality gates`

Exit evidence:

- Frontend install, lint, unit tests, and production build pass.
- API client envelope and error parsing tests pass.
- Auth, consent, diagnostic, lesson, learner dashboard, parent dashboard, and
  protected-route journeys are covered.
- Accessibility, mobile viewport, loading, empty, failure, retry, PWA, and
  low-data behavior are verified to the agreed beta scope.

### Gate 6: CI/CD, Environments, Observability, And Operations

Goal: make deployment targets, operational signals, and support procedures
match what the release process expects.

TODO sections:

- `11. Observability, metrics, logging, tracing, and alerting`
- `12. CI/CD, infrastructure, deployment, Docker, and environments`
- `16. Incident response, operations, and support`

Exit evidence:

- CI branch names, deployment targets, required checks, and workflow triggers are
  aligned.
- Docker images build, run, and meet non-root and secret-handling expectations.
- Staging environment variables and secret requirements are documented.
- Metrics, dashboards, alerts, logs, traces, incident response, emergency
  controls, and support workflows have tests, scripts, screenshots, runbooks, or
  review evidence as appropriate.

### Gate 7: Commercial, Notifications, Legal, And Beta Scope

Goal: close the non-code release blockers that affect users, guardians,
payments, communication, and public claims.

TODO sections:

- `9. Billing, subscriptions, payments, and monetization`
- `10. Notifications and communication`
- `18. Beta launch, staging acceptance, and product scope`

Exit evidence:

- Billing provider scope is either implemented and tested or explicitly removed
  from beta scope.
- Webhooks, pricing rules, billing UX, and failure paths are covered if billing
  is in scope.
- Email/SMS/provider templates, unsubscribe rules, delivery controls, and audit
  logs are verified if notifications are in scope.
- Privacy Policy, Terms of Service, Parent Consent Notice, and child-friendly
  Privacy Notice are drafted, reviewed, and linked.
- Public beta scope is narrow, explicit, and consistent across docs and UI.

### Gate 8: Release Evidence And Go/No-Go

Goal: convert verified work into a release decision package.

TODO sections:

- `14. Testing, release evidence, and quality gates`
- `18. Beta launch, staging acceptance, and product scope`
- `20. Final release-blocker checklist`

Exit evidence:

- Backend, frontend, E2E, security, migration, backup/restore, and staging smoke
  evidence are attached.
- OpenAPI hash, image digests, SBOM, changelog, migration revision, deployment
  manifest, and rollback evidence are recorded.
- Release evidence validation passes.
- Rollback is tested.
- Go/no-go review is completed by the named release owner.

## Recommended Batch Order

Work in small batches. Each batch should be independently reviewable and should
update TODO status only for items it can prove.

1. Repo governance and repo-state verification.
2. PR-002R runtime/API contract cleanup.
3. Router registration, legacy route exclusion, route inventory, and OpenAPI.
4. API envelope and error-envelope standardization.
5. Auth, token, cookie, RBAC, and object-authorization negative tests.
6. POPIA consent, data-rights, audit integrity, and legal/privacy docs.
7. Database migrations, schema integrity, transactions, and repositories.
8. Backup/restore dry run, Redis recoverability, RPO/RTO.
9. LLM gateway, PII redaction, output validators, and safe refusal fixtures.
10. CAPS scope, item schema, item-bank approval, diagnostics, and mastery proof.
11. Frontend API client, auth/consent UX, learner/guardian journeys.
12. Accessibility, mobile, PWA, low-data, and Playwright staging E2E.
13. CI/CD alignment, Docker hardening, environment contracts, staging.
14. Observability, alerts, incident response, support, and emergency controls.
15. Billing and notifications, either verified or explicitly excluded from beta.
16. Release evidence bundle, rollback test, and go/no-go review.

## Status Update Pattern

When closing a batch, update `TODO.md` using this shape:

```text
- [verify] `P0` Short task name. Evidence: source/test/workflow paths.
  Verification gap: exact command, CI job, staging evidence, or review record
  still required.

- [x] `P0` Short task name. Evidence: source/test/workflow paths;
  `command ...` passed on YYYY-MM-DD.
```

## Anti-Patterns To Avoid

- Do not mark a broad section `[x]` because many tests exist nearby.
- Do not call generated artifacts release evidence unless a validation command
  proves them against the current commit.
- Do not let historical reports override `docs/current_state.md`.
- Do not claim full CAPS, diagnostics, accessibility, security, or beta
  readiness until the exact launch scope has passing evidence.
- Do not mix product expansion work into release-blocker batches unless it
  removes a blocker.

## First Five Pull Requests

1. **Repo Truth PR**: repository governance, repo-state script, Make target,
   CI hook, and current-state links.
2. **Runtime Contract PR**: PR-002R docs, router cleanup, runtime tests,
   route inventory, OpenAPI drift, envelope/error contract.
3. **Privacy Boundary PR**: object authorization, consent gates, POPIA negative
   tests, audit completeness, data-rights docs.
4. **Persistence Resilience PR**: migrations, schema integrity, repository
   tests, backup/restore dry run, RPO/RTO.
5. **Learning Evidence PR**: item schema, IRT granular reconciliation, item-bank
   approval scope, diagnostic session lifecycle, mastery evidence.

