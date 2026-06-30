# EduBoost V2 Audit Remediation Roadmap

**Document version:** 2.0  
**Generated:** 2026-06-13  
**Source audit:** `audits/reports/Technical_Audit_Report_2026-06-13.md`  
**Prior roadmap:** repository version preceding this document  
**Release posture:** **NO-GO** until every non-waivable gate is green, all other P0 work is complete, and any permitted P1/P2 deferral has an approved, unexpired exception.  
**Primary objective:** restore clean-checkout reproducibility, repair privacy and API contracts, make CI and security gates truthful, prove the identity of the release environment, and reassess controlled-beta readiness from attributable evidence.

---

## 1. Document Control And Verification Status

This roadmap is both an execution plan and a release-control document. Mutable verification results must be tied to an exact source state rather than treated as timeless facts.

| Field | Value |
| --- | --- |
| Verified branch | `TBD in AR-000` |
| Verified commit SHA | `TBD in AR-000` |
| Verification timestamp | `TBD in AR-000` |
| Verification operator or CI run | `TBD in AR-000` |
| Worktree state | `TBD in AR-000` |
| Canonical environment | `TBD in AR-011` |
| Roadmap owner | `TBD before remediation begins` |
| Final release approver | `TBD before Phase 1 closes` |

The recovery facts below are retained from the prior roadmap, but they are not release evidence until AR-000 records the branch, commit, operator, and supporting evidence paths.

---

## 2. Material Changes In Version 2.0

This version incorporates the review findings and strengthens the roadmap in the following ways:

- Splits Content Factory work into **registry restoration** and **generated-artifact/bootstrap policy** so the mostly completed recovery cannot hide eight remaining failures.
- Resolves the `make test-fast` contradiction: registry work can close independently, but **Phase 1 cannot close until the complete fast gate is green**.
- Splits frontend environment correctness from lint/tooling cleanup, making production API configuration a P0 control.
- Elevates dependency-scan enforcement and canonical-environment auditability to P0.
- Replaces team-only ownership with a required **DRI, approver, milestone, evidence link, and current blocker** for every workstream.
- Defines formal, expiring exceptions and explicitly lists gates that may never be waived.
- Makes database, container, Playwright, workflow, OpenAPI, and dependency-scan verification commands unambiguous and safer.
- Adds operational observability, privacy-safe logging, alerting, deprecation telemetry, and rollback requirements for repaired flows.
- Requires explicit pytest files or registered markers and a non-zero test-count assertion for release-critical suites.
- Breaks auth consolidation into smaller reviewable increments.
- Separates the durable plan from mutable status and removes local-machine file paths from provenance.

---

## 3. Current Recovery Snapshot

### 3.1 Content Factory registry

The previous roadmap records that housekeeping commit `6b3c2196` deleted the full registry and that the two policy files were restored from `6b3c2196^`.

| File | Recorded count | Recorded SHA-256 | Recorded provenance |
| --- | ---: | --- | --- |
| `data/content_factory/scopes.json` | 51 scopes | `a9cb8033ff875e78514bb8c4f6116adeaac3f9999aa7ddcb23464627b888922e` | `6b3c2196^` |
| `data/content_factory/coverage_targets.json` | 805 targets | `18015ee14ca8edc8e5cd55460b31e63c46a96749c74806c9c1d474bdb7357e76` | `6b3c2196^` |

Recorded focused check:

```bash
.venv/bin/python -m pytest -q tests/unit/test_content_scope_registry.py --no-cov
```

Recorded result: `6 passed`.

Recorded broader Content Factory slice:

```bash
.venv/bin/python -m pytest -q \
  tests/unit/test_content_scope_registry.py \
  tests/unit/test_source_inventory_expansion.py \
  tests/unit/test_source_manifest_readiness.py \
  tests/unit/test_study_material_expansion_foundation.py \
  tests/unit/test_scope_content_builder.py \
  --no-cov
```

Recorded result: `18 passed, 1 skipped, 8 failed`.

Those eight failures must not be dismissed as registry failures or solved by casually changing expected counts. They indicate a second problem layer involving ignored generated artifacts, bootstrap behavior, source/readiness assumptions, or launch-slice policy drift.

Expected `.gitignore` contract:

```gitignore
data/content_factory/*
!data/content_factory/scopes.json
!data/content_factory/coverage_targets.json
```

### 3.2 Status rule

A result in this snapshot becomes authoritative only when AR-000 records:

- branch and commit SHA;
- clean or intentionally dirty worktree state;
- command and exit code;
- test count and duration;
- operator or CI run;
- evidence-file or artifact link.

---

## 4. Scope

### In scope

- Content Factory registry reproducibility.
- Generated Content Factory artifact and bootstrap policy.
- Backend fast-gate failures exposed after registry restoration.
- POPIA `AuthContext` versus dictionary-shaped actor mismatch.
- Frontend/backend POPIA route drift.
- POPIA operational telemetry and privacy-safe auditability.
- CI duplicate job IDs, invalid `needs`, package-manager drift, and lockfile ownership.
- Stale OpenAPI output and missing client-contract enforcement.
- Production frontend API configuration and fail-closed behavior.
- Frontend lint and environment-check toolchain failures.
- Non-enforcing dependency vulnerability scans and broken reporting.
- Stripe customer identity placeholder behavior.
- Backend async-mock and frontend React warning debt.
- Auth and token ownership fragmentation.
- Generated evidence provenance and dirty-worktree ambiguity.
- Canonical environment identity, access, and reproducibility.
- Release rollback, observability, and approval evidence.

### Out of scope unless required to close a listed risk

- New grades, subjects, markets, or product expansion.
- Broad UI redesign.
- New billing functionality beyond identity correctness and safe failure behavior.
- Refactors with no direct release-risk reduction or gate-enabling outcome.

---

## 5. Audit-Finding Traceability

| Audit concern | Roadmap coverage | Release significance |
| --- | --- | --- |
| Required Content Factory registry files missing or ignored | AR-001A, AR-001B | Clean-checkout reproducibility and backend fast gate |
| POPIA service fails with injected `AuthContext` | AR-002 | Non-waivable privacy correctness |
| Frontend and backend POPIA routes disagree | AR-003, AR-005 | End-to-end privacy operations and API contract |
| Duplicate CI job ID and npm/pnpm mismatch | AR-004 | Truthful, executable required checks |
| Stale OpenAPI document | AR-005 | Backend/frontend contract integrity |
| Frontend lint and env-check commands fail | AR-006A, AR-006B | Production configuration safety and developer/CI toolchain |
| Dependency scans suppress failures or report incorrectly | AR-007 | Non-waivable critical/high vulnerability control |
| Billing sends a placeholder customer email | AR-008 | Identity correctness and privacy-safe provider integration |
| Async mock and React test warnings | AR-009 | Test reliability and hidden async defects |
| Canonical verification environment could not be reached | AR-010 | Exact-release identity and staging auditability |
| Authentication/token behavior is fragmented | AR-011A, AR-011B, AR-011C | Maintainability and future security regression prevention |
| Generated evidence and dirty worktree obscure provenance | AR-000, AR-012 | Trustworthy release evidence |
| Repaired flows need operational proof and rollback | AR-013 | Safe operation after deployment |
| Full release readiness requires one exact-commit decision | AR-014 | Controlled-beta GO/NO-GO governance |

---

## 6. Execution Rules

1. **Executable checks are authoritative.** Documentation cannot override a failing command.
2. **A release gate must fail closed.** `continue-on-error`, `|| true`, ignored exit codes, or equivalent suppression require an approved exception unless explicitly prohibited below.
3. **Every workstream has one DRI.** Teams may contribute, but accountability is never shared ambiguously.
4. **Every closure claim has evidence.** Evidence must identify the exact commit, environment, command, result, and approver.
5. **Small reviewable changes are preferred.** Large refactors must be split into independently testable PRs.
6. **Compatibility aliases are temporary controls.** They must share canonical authorization and service logic, be deprecated in OpenAPI, emit usage metrics, and have a removal milestone.
7. **Generated evidence is produced only from an identified source tree.** Final release evidence must come from a clean checkout.
8. **Test count matters.** A release-critical test command that selects zero tests, unexpectedly fewer tests, or only mocked contract tests fails the gate.
9. **Privacy-safe observability is required.** Logs and metrics must not expose plaintext personal data, tokens, secrets, exports, correction content, or erasure payloads.
10. **Preserve currently green controls.** Migration graph, schema integrity, import boundaries, security contracts, privacy-boundary checks, TypeScript, and Vitest must not regress.
11. **Newly exposed failures remain visible.** CI repairs may reveal additional defects; those defects must be owned rather than suppressed.
12. **GO requires agreement across layers.** Code, CI, OpenAPI, frontend, staging identity, security, privacy/legal, content, rollback, and release approval must agree on the same release commit and image.

---

## 7. Priority And Exception Policy

### 7.1 Priority definitions

| Priority | Meaning |
| --- | --- |
| P0 | Release blocker. Must be complete before controlled-beta readiness is reassessed. |
| P1 | Release-candidate hardening. Must be complete unless a permitted, approved, unexpired exception exists. |
| P2 | Maintainability or evidence debt. May be deferred only when it does not undermine a P0/P1 gate and has an owner, risk statement, and target milestone. |

### 7.2 Required exception record

Every permitted exception must contain:

- affected AR ID and failed acceptance criterion;
- exact failed command or missing evidence;
- business justification;
- user, privacy, security, operational, and release impact;
- compensating control;
- DRI and approving authority;
- creation and expiry dates;
- target fix milestone;
- containment and rollback plan;
- evidence that the exception itself is monitored;
- confirmation that the item is not in the non-waivable list.

Exceptions expire automatically. An expired exception is equivalent to a failed gate.

### 7.3 Non-waivable gates

The following may not be waived for controlled beta:

- POPIA export, erasure, erasure cancellation, correction, and restriction correctness for supported flows.
- Authentication or authorization bypass, object-level authorization failure, or fail-open identity behavior.
- Unknown or unprovable release commit, image digest, migration head, or staging identity.
- Critical or high unaccepted production dependency vulnerability.
- Secrets exposed in source, artifacts, logs, images, or CI output.
- Non-reproducible required Content Factory registry inputs.
- Production frontend configuration that can target an unintended backend.
- Fabricated billing identity data sent to Stripe or another provider.
- Non-reproducible release artifacts or evidence that cannot be tied to a clean commit.
- A failed rollback rehearsal for the release candidate.

---

## 8. Workstream Register

All `TBD` ownership and schedule fields must be completed during AR-000. A workstream may not move to `In progress` without a DRI and target milestone.

| ID | Workstream | Priority | DRI | Approver | Target milestone | Depends on | Status | Current blocker | Evidence link |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| AR-000 | Establish baseline, ownership, and evidence discipline | P0 | TBD | Release owner | M0 | None | Pending | Ownership and exact source state unrecorded | TBD |
| AR-001A | Restore and validate registry source of truth | P0 | TBD | Content owner | M1 | AR-000 | In progress | Preflight, CI/container reproduction, attributable evidence | TBD |
| AR-001B | Define generated-artifact bootstrap and reconcile Content Factory failures | P0 | TBD | Backend + Content approvers | M1 | AR-001A | Pending | Eight recorded failures and undefined artifact policy | TBD |
| AR-002 | Normalize POPIA actor/auth context | P0 | TBD | Privacy owner | M1 | AR-000 | Pending | `AuthContext`/dict service mismatch | TBD |
| AR-003 | Reconcile POPIA frontend/backend routes and operations | P0 | TBD | Privacy + API approvers | M1 | AR-002 | Pending | Active client paths do not match router | TBD |
| AR-004 | Repair CI workflows, pnpm ownership, and workflow validation | P0 | TBD | Platform owner | M1 | AR-000 | Pending | Duplicate job ID and npm/pnpm drift | TBD |
| AR-005 | Regenerate and enforce OpenAPI/client contracts | P0 | TBD | API owner | M1 | AR-003, AR-004 | Pending | Stale spec and no complete client contract check | TBD |
| AR-006A | Enforce production frontend API configuration | P0 | TBD | Platform owner | M1 | AR-004 | Pending | Production-looking fallback can mask missing config | TBD |
| AR-006B | Repair frontend lint and portable env-check tooling | P1 | TBD | Frontend owner | M2 | AR-004, AR-006A | Pending | Unsupported lint flag and interpreter assumption | TBD |
| AR-007 | Enforce dependency vulnerability policy and reporting | P0 | TBD | Security owner | M1 | AR-004 | Pending | Scans suppress failures and reporting is broken | TBD |
| AR-008 | Correct Stripe customer identity handling | P1 | TBD | Billing + Privacy approvers | M2 | AR-002 | Pending | Fabricated placeholder email | TBD |
| AR-009 | Eliminate backend/frontend test-warning debt | P1 | TBD | QA owner | M2 | AR-001B, AR-002, AR-006B | Pending | Unawaited coroutine and React `act` warnings | TBD |
| AR-010 | Re-establish environment auditability from the local WSL source workspace | P0 | TBD | Release owner | M1 | AR-000, AR-004 | Pending | Remote VM inaccessible; staging identity still unproven | TBD |
| AR-011A | Define canonical auth/token contract and characterization tests | P2 | TBD | Security owner | M3 | AR-002, AR-005 | Pending | Multiple active token/auth paths | TBD |
| AR-011B | Migrate callers and isolate legacy auth behavior | P2 | TBD | Security owner | M3 | AR-011A | Pending | Compatibility paths and monkey patches | TBD |
| AR-011C | Remove retired auth paths and enforce architecture boundaries | P2 | TBD | Architecture approver | M3 | AR-011B | Pending | Legacy imports remain possible | TBD |
| AR-012 | Make generated evidence reproducible and attributable | P2 | TBD | Release owner | M2 | AR-000, AR-004 | Pending | Dirty generated files and unclear provenance | TBD |
| AR-013 | Add operational observability and rollback controls | P0 | TBD | Operations + Privacy approvers | M2 | AR-002, AR-003, AR-008, AR-010 | Pending | Repaired flows lack complete operational acceptance | TBD |
| AR-014 | Run full release-candidate verification and decide GO/NO-GO | P0 | TBD | Final release approver | M4 | See Section 18 | Blocked | Upstream gates incomplete | TBD |

### Milestone intent

| Milestone | Purpose |
| --- | --- |
| M0 | Baseline, DRI assignment, source identity, evidence locations |
| M1 | Immediate blockers: reproducibility, privacy contracts, CI, OpenAPI, production config, security scans, environment identity |
| M2 | Release hardening: frontend tooling, billing identity, warning cleanup, evidence, observability, rollback |
| M3 | Auth maintainability work that may be deferred only when it does not undermine release correctness |
| M4 | Exact-commit release verification and GO/NO-GO decision |

Calendar dates or sprint numbers must be assigned in AR-000. Milestone labels alone are not sufficient for active execution.

---

## 9. Phase 0 — Baseline, Ownership, And Evidence Discipline

### AR-000: Establish the remediation baseline

**Goal:** make every later claim traceable to one commit, one branch, one operator or CI run, and one execution environment.

#### Actions

- Create or identify the remediation branch from the intended `master` commit.
- Record branch, commit SHA, remotes, worktree state, operating system, Python version, Node version, Corepack version, pnpm version, Docker version, and Compose version.
- Preserve the audit and this roadmap in repository-relative paths.
- Record pre-fix outputs for backend fast tests, OpenAPI drift, frontend lint, frontend env-check, workflow validation, dependency scans, and canonical-environment access.
- Assign a DRI, approver, target date or sprint, and evidence path for every AR item.
- Create a residual-defect register with defect ID, severity, affected test or gate, DRI, milestone, and release-blocking status.
- Freeze final evidence refreshes until the source tree is clean.

#### Acceptance

- [ ] `git status --short`, `git rev-parse HEAD`, `git branch --show-current`, and `git remote -v` are recorded.
- [ ] Toolchain versions and execution environment are recorded.
- [ ] Audit, roadmap, baseline logs, and residual-defect register use repository-relative or CI-artifact references.
- [ ] Every workstream has one DRI, one approver, and one calendar target or sprint.
- [ ] Baseline failures and test counts are attached before fixes are marked complete.
- [ ] Release evidence refresh rules are documented.

**Evidence target:** `docs/release/ar_000_audit_remediation_baseline.md`

---

## 10. Phase 1 — Immediate Release Blockers

### AR-001A: Restore and validate the Content Factory registry source of truth

**Problem:** runtime code requires `data/content_factory/scopes.json` and `data/content_factory/coverage_targets.json`, while repository history and ignore rules allowed those required inputs to disappear from a clean checkout.

**Decision:** treat the two registry files as versioned product/curriculum policy for this remediation. Replacing them with generated inputs requires a separate Content-owned ADR and byte-for-byte or semantically equivalent reproducibility proof across local development, CI, containers, and staging.

#### Actions

- Confirm both files are Git-tracked in the remediation commit.
- Confirm `.gitignore` allows only required policy inputs while ignoring generated siblings.
- Add `make content-factory-preflight` or an equivalent script that validates:
  - file presence;
  - JSON schema;
  - duplicate identifiers;
  - referential and semantic consistency;
  - expected minimum counts without hard-coding obsolete launch policy;
  - deterministic SHA-256 reporting.
- Add actionable failure messages with setup guidance.
- Run the preflight in local setup, `make test-fast`, CI, container build or startup validation, seed commands, and staging readiness.
- Record hashes and source provenance in release evidence.

#### Acceptance

- [ ] A clean checkout contains both registry files as tracked files.
- [ ] Removing, corrupting, or semantically invalidating either file makes preflight fail with a clear message.
- [ ] Local, CI, container, and staging paths report identical hashes for the same release commit.
- [ ] Focused registry tests pass.
- [ ] Registry evidence identifies commit, operator or CI run, time, and hash.

#### Required checks

```bash
git ls-files --error-unmatch \
  data/content_factory/scopes.json \
  data/content_factory/coverage_targets.json

for path in \
  data/content_factory/scopes.json \
  data/content_factory/coverage_targets.json; do
  if git check-ignore -q "$path"; then
    echo "Required registry file is incorrectly ignored: $path" >&2
    exit 1
  fi
done

make content-factory-preflight
.venv/bin/python -m pytest -q tests/unit/test_content_scope_registry.py --no-cov
```

The ignore-rule assertion should also be implemented inside the preflight script so local and CI behavior remain identical.

**Evidence target:** `docs/release/ar_001a_content_factory_registry_evidence.md`

### AR-001B: Define generated-artifact bootstrap and reconcile remaining Content Factory failures

**Problem:** after registry restoration, the broader Content Factory slice still records eight failures involving generated artifacts, bootstrap assumptions, source readiness, or status/count expectations.

#### Actions

- Classify every required artifact as one of:
  - versioned deterministic fixture;
  - deterministic build output;
  - downloaded external artifact with checksum and license record;
  - non-required local output.
- Define one bootstrap command that creates or retrieves all required non-versioned artifacts from a clean checkout.
- Run the same bootstrap logic in local setup, CI, containers, and staging.
- Create a defect record for each remaining failing test or failure cluster.
- Require Content-owner approval for any changed curriculum scope, readiness status, target count, or launch-slice expectation.
- Prohibit changing expected counts solely to make tests pass.
- Add fixture/version metadata so tests can identify the policy version they assert.
- Rerun the focused slice and full fast gate.

#### Acceptance

- [ ] Every required artifact has an approved lifecycle classification.
- [ ] A clean checkout can bootstrap required artifacts without access to a developer's untracked filesystem.
- [ ] Focused Content Factory tests pass against the approved policy version.
- [ ] Count or readiness changes have a linked Content decision, rationale, and reviewer.
- [ ] No residual Content Factory failure is hidden or reclassified without a defect ID.
- [ ] `make test-fast` passes before Phase 1 can close.

#### Required checks

```bash
make content-factory-bootstrap
make content-factory-preflight

.venv/bin/python -m pytest -q \
  tests/unit/test_content_scope_registry.py \
  tests/unit/test_source_inventory_expansion.py \
  tests/unit/test_source_manifest_readiness.py \
  tests/unit/test_study_material_expansion_foundation.py \
  tests/unit/test_scope_content_builder.py \
  --no-cov

make test-fast
```

**Closure rule:** AR-001B may close only when the generated-artifact policy is implemented and its focused tests pass. Phase 1 remains open until the complete `make test-fast` gate is green. Merely assigning residual failures does not satisfy the Phase 1 exit gate.

**Evidence target:** `docs/release/ar_001b_content_factory_bootstrap_evidence.md`

### AR-002: Normalize POPIA actor and authentication context

**Problem:** the active router injects `AuthContext`, while `POPIADataRightsService` expects dictionary-shaped actors and calls `.get(...)`, allowing authenticated privacy routes to fail before authorization or persistence.

#### Actions

- Introduce one typed `ActorContext` or equivalent containing actor ID, subject ID, roles, authentication source, and narrowly scoped raw claims when required.
- Convert `AuthContext` and any supported legacy claim dictionaries at one explicit boundary.
- Remove `Any` and direct `.get(...)` access from POPIA service interfaces.
- Fail closed when identity, role, learner ownership, consent, or legal-hold data is absent.
- Add real dependency-injection tests for export, erasure request, erasure cancellation, correction, restriction, and erasure execution.
- Cover guardian/learner relationship, admin or authorised staff rules, unauthorized, forbidden, validation, not found, legal hold, idempotency, audit transitions, and provider/database failure.
- Register a dedicated pytest marker such as `popia_routes` and configure the release command to fail when zero tests are selected.

#### Acceptance

- [ ] POPIA service interfaces accept a bounded typed actor model.
- [ ] Real FastAPI dependency-injection tests pass with production-equivalent `AuthContext` semantics.
- [ ] Supported operations return expected success or policy-denial responses, never actor-shape 500s.
- [ ] Missing or unauthorized identity fails closed.
- [ ] Audit events capture normalized actor identity without raw tokens or unnecessary personal data.
- [ ] Release-critical POPIA test selection executes the expected minimum test count.

#### Required checks

```bash
.venv/bin/python scripts/assert_pytest_marker_count.py \
  --marker popia_routes \
  --minimum 1

.venv/bin/python -m pytest -q -m popia_routes --no-cov
```

If `scripts/assert_pytest_marker_count.py` does not exist, AR-002 includes adding an equivalent zero-test and minimum-count guard.

**Evidence target:** `docs/release/ar_002_popia_actor_context_evidence.md`

### AR-003: Reconcile POPIA frontend/backend routes and operations

**Problem:** frontend services and parent-dashboard privacy links call route shapes that the active backend does not expose.

#### Canonical routes

- `POST /popia/exports`
- `POST /popia/erasure`
- `POST /popia/erasure/{learner_id}/cancel`
- `POST /popia/correction`
- `POST /popia/restriction`

The final prefix must be derived from the canonical FastAPI runtime and OpenAPI document rather than duplicated inconsistently in clients.

#### Actions

- Update frontend service methods, HTTP methods, paths, request bodies, and response handling to canonical contracts.
- Update backend-generated parent links to canonical frontend actions or tested API aliases as appropriate; do not expose mutation endpoints as blind navigation links.
- Decide whether deletion status is a supported product requirement. Implement and document it, or remove the unsupported client method and UI affordance.
- Implement compatibility aliases only when migration requires them; route aliases through the same service, authorization, audit, and schemas.
- Mark aliases deprecated in OpenAPI, emit usage metrics, create a removal issue, and assign a target date.
- Add integration/E2E coverage for success, unauthorized, forbidden, validation, not found, legal hold, and cancellation transitions.

#### Acceptance

- [ ] Every active frontend POPIA operation maps to a backend OpenAPI operation.
- [ ] HTTP method, full path, auth requirements, request schema, response schema, and error responses agree.
- [ ] Parent-dashboard actions are covered by integration or E2E tests.
- [ ] Deprecated aliases have metrics, owner, removal issue, and deadline.
- [ ] Privacy workflows do not expose personal payloads in URLs, logs, or analytics.

**Evidence target:** `docs/release/ar_003_popia_route_contract_evidence.md`

### AR-004: Repair CI workflow mechanics and package ownership

**Problem:** the main workflow contains a duplicate job ID and runs npm against a pnpm-managed frontend without the required npm lockfiles.

#### Actions

- Rename schema jobs to unique IDs such as `schema-integrity` and `schema-drift-live`.
- Validate workflows with a duplicate-key-aware YAML parser and `actionlint`.
- Add repository-specific validation for:
  - duplicate mapping keys;
  - invalid `needs` references;
  - missing lockfiles;
  - forbidden `npm ci` in pnpm-owned packages;
  - release gates using `continue-on-error` or unconditional `|| true`;
  - stale required-check names after job renames.
- Standardize frontend and E2E installation on Corepack and the pinned pnpm version.
- Use `pnpm-lock.yaml` and frozen-lockfile installation.
- Decide Playwright ownership explicitly:
  - preferred: `app/frontend` owns Playwright and its configuration; or
  - alternative: add a root workspace manifest and root pnpm lockfile.
- Update branch protection and required checks after job renames.

#### Acceptance

- [ ] Duplicate-key-aware validation and `actionlint` pass.
- [ ] No CI job invokes a package manager without the matching manifest and lockfile.
- [ ] Frontend and E2E jobs use the declared pnpm version and frozen lockfile.
- [ ] All `needs` references and required-check names resolve.
- [ ] CI reaches backend, frontend, schema, OpenAPI, security, container, and E2E checks.
- [ ] A clean CI run on the remediation branch is linked.

#### Required checks

```bash
actionlint
.venv/bin/python scripts/validate_github_workflows.py
corepack enable
corepack pnpm --dir app/frontend install --frozen-lockfile
```

If `actionlint` is not already available in the supported toolchain, AR-004 must install a pinned version in CI or run it from a pinned container image.

**Evidence target:** `docs/release/ar_004_ci_repair_evidence.md`

### AR-005: Regenerate and enforce OpenAPI and frontend client contracts

**Problem:** `docs/openapi.json` is stale, and current frontend/API drift demonstrates that path-only or mocked-client tests are insufficient.

#### Actions

- Complete AR-002 and AR-003 before final regeneration.
- Generate OpenAPI from the canonical runtime entrypoint.
- Review the diff for accidental route exposure, duplicate prefixes, deprecated aliases, auth requirements, privacy schemas, and response models.
- Add deterministic OpenAPI drift checking to required CI.
- Generate or maintain a frontend operation manifest tied to OpenAPI operation IDs.
- Validate for each active client operation:
  - HTTP method;
  - normalized path and prefix;
  - security requirement;
  - request body or query schema;
  - success response schema;
  - expected error response schemas.
- Record OpenAPI hash and generator version.

#### Acceptance

- [ ] `scripts/generate_openapi.py --check` passes from a clean checkout.
- [ ] POPIA routes, auth requirements, schemas, and deprecated aliases are represented correctly.
- [ ] Frontend contract tests verify more than path existence.
- [ ] Generation is deterministic for the same commit and toolchain.
- [ ] The OpenAPI hash is included in release evidence.

#### Required checks

```bash
.venv/bin/python scripts/generate_openapi.py
.venv/bin/python scripts/generate_openapi.py --check
corepack pnpm --dir app/frontend run api-contract-check
```

**Evidence target:** `docs/release/ar_005_openapi_contract_evidence.md`

### AR-006A: Enforce production frontend API configuration

**Problem:** a production-looking hosted API fallback can cause a build with missing configuration to target an unintended backend.

#### Actions

- Centralize API-base resolution in one frontend module.
- Require `NEXT_PUBLIC_API_URL` for production build and startup.
- Allow localhost fallback only in explicit development mode.
- Validate scheme, host, API prefix, trailing-slash normalization, and localhost prohibition in production.
- Add unit and build-time tests for missing, malformed, wrong-prefix, localhost-in-production, and unintended-host values.
- Record the expected staging/production API origin in deployment evidence without secrets.

#### Acceptance

- [ ] Production build without `NEXT_PUBLIC_API_URL` fails closed.
- [ ] Production cannot silently target the hosted fallback or localhost.
- [ ] All frontend API clients use the same validated resolver.
- [ ] Deployment evidence identifies the expected API origin and release environment.

**Evidence target:** `docs/release/ar_006a_frontend_api_environment_evidence.md`

### AR-007: Enforce dependency vulnerability policy and reporting

**Problem:** Python and pnpm audit commands suppress failure, and the scan-report upload references a nonexistent step.

#### Actions

- Define blocking thresholds for production and development dependencies.
- Remove unconditional `|| true` and equivalent release-gate suppression.
- Add an approved exception file containing package, advisory, affected versions, owner, justification, compensating control, approval, and expiry.
- Repair SARIF or artifact upload using supported actions and valid step outputs.
- Scan the exact Python environment and pnpm lockfile used in production builds.
- Add a controlled scanner-policy test fixture that proves a seeded high-severity advisory fails without modifying production lockfiles.
- Retain machine-readable and human-readable reports.

#### Acceptance

- [ ] A controlled high-severity fixture fails the scan job.
- [ ] Critical/high unaccepted production findings block release.
- [ ] Exceptions are explicit, approved, monitored, and expiring.
- [ ] Reports upload successfully and are linked from CI.
- [ ] Scanner errors fail the job rather than appearing as clean results.

**Evidence target:** `docs/security/ar_007_dependency_scan_enforcement.md`

### AR-010: Re-establish environment auditability from the local WSL source workspace

**Problem:** the audit could not reach the previously designated remote environment, and the project decision is now that the local WSL checkout is the main working directory and source-of-truth workspace. Release verification cannot rely on the old remote VM unless access and identity evidence are re-established.

#### Actions

- Treat `/home/nkgolol/Dev/Development/Eduboost-V2` as the source workspace for remediation, audit, and release-evidence preparation.
- Keep the old remote VM classified as inaccessible and non-canonical unless access is restored and this workstream records fresh identity evidence.
- Document the local WSL workspace decision in operations docs and link it from the README.
- For any future staging or remote environment, restore access for at least two authorized operators or document the approved replacement environment.
- Add a read-only identity command or endpoint that records:
  - commit SHA;
  - container image digest;
  - application version;
  - migration head;
  - OpenAPI hash;
  - Content Factory registry hashes;
  - sanitized configuration fingerprint;
  - environment name.
- Prove staging does not depend on untracked local Content Factory data.
- Document build-to-deploy provenance from CI artifact to running environment.

#### Acceptance

- [ ] The repository documents the local WSL checkout as the current source workspace and the old remote VM as inaccessible/non-canonical.
- [ ] The release owner and a second authorized operator can identify and verify any environment used for staging or release evidence.
- [ ] Environment identity matches the intended commit, image, migration head, OpenAPI hash, and registry hashes.
- [ ] Staging startup succeeds without developer-local untracked files.
- [ ] Build and deployment provenance is attached.
- [ ] Unknown or mismatched identity blocks release automatically or procedurally.

**Evidence target:** `docs/operations/ar_010_canonical_environment_evidence.md`

### Phase 1 exit gate

Phase 1 closes only when all of the following are true:

- [ ] AR-001A, AR-001B, AR-002, AR-003, AR-004, AR-005, AR-006A, AR-007, and AR-010 are complete.
- [ ] `make test-fast` passes in full.
- [ ] POPIA real-route tests pass and execute the expected minimum test count.
- [ ] OpenAPI drift and frontend operation-contract checks pass.
- [ ] Production frontend API configuration fails closed when missing or unsafe.
- [ ] Dependency scanning blocks unaccepted critical/high production findings.
- [ ] Workflow validation and `actionlint` pass.
- [ ] The canonical verification environment is accessible and its identity matches the release candidate.
- [ ] A required-check CI run passes on the exact remediation commit.

Assigning a residual defect does not make a failed Phase 1 gate green.

---

## 11. Phase 2 — Release-Candidate Hardening

### AR-006B: Repair frontend lint and portable environment-check tooling

#### Actions

- Replace unsupported `next lint --no-cache` with direct ESLint or another command supported by the pinned stack.
- Replace the implicit `python` frontend-script dependency with a portable Node implementation or a documented repo command using the supported Python interpreter.
- Keep API configuration checks in AR-006A; use this workstream for toolchain portability and developer feedback.
- Run env-check, lint, type-check, unit tests, and production build in one CI job after installation.

#### Acceptance

- [ ] `pnpm run env-check` passes locally and in CI with the documented toolchain.
- [ ] `pnpm run lint`, `type-check`, `test`, and `build` pass.
- [ ] No frontend command silently switches to npm.
- [ ] CI logs show the pinned Node and pnpm versions.

**Evidence target:** `docs/release/ar_006b_frontend_toolchain_evidence.md`

### AR-008: Correct Stripe customer identity handling

#### Actions

- Resolve the authenticated guardian/customer identity at the billing service boundary.
- Decrypt and normalize email only when authorized and required.
- Omit provider email when unavailable rather than sending fabricated data.
- Store stable internal customer metadata suitable for reconciliation without exposing sensitive data.
- Add idempotent customer lookup/creation and retry behavior.
- Verify provider failures do not leave inconsistent internal billing state.
- Add privacy-safe structured events and provider-error metrics.

#### Acceptance

- [ ] No production checkout sends `billing-placeholder` or other fabricated email.
- [ ] Stripe customer metadata contains a stable, non-secret internal identity.
- [ ] Plaintext email, tokens, and provider secrets are absent from logs.
- [ ] Tests cover valid email, unavailable email, invalid email, duplicate checkout, retry, provider timeout, and provider failure.
- [ ] Billing failure rates and provider errors are observable without personal-data leakage.

**Evidence target:** `docs/release/ar_008_billing_identity_evidence.md`

### AR-009: Eliminate backend and frontend test-warning debt

#### Actions

- Replace `AsyncMock` with `Mock` for synchronous SQLAlchemy/session methods.
- Await genuine async collaborators.
- Treat unawaited coroutine warnings as errors in focused backend suites, then expand to release suites.
- Fix frontend tests with Testing Library async helpers so state updates are awaited.
- Make React `act(...)` warnings fail the relevant test job after cleanup.
- Keep any temporary warning suppression narrow, documented, owned, and expiring.

#### Acceptance

- [ ] POPIA and adjacent backend tests run without unawaited coroutine warnings.
- [ ] Backend release suites fail on unawaited coroutine warnings.
- [ ] Frontend test output contains no unresolved React `act(...)` warnings.
- [ ] Any remaining suppression has an approved exception and expiry.

**Evidence target:** `docs/release/ar_009_test_warning_evidence.md`

### AR-012: Make generated evidence reproducible and attributable

#### Actions

- Inventory generated files and classify each as:
  - committed deterministic artifact;
  - CI-retained artifact;
  - local disposable output.
- Provide one command to regenerate committed evidence and another to verify without modifying files.
- Embed source commit, generator version, input hashes, and normalized timestamp metadata.
- Move volatile logs, screenshots, and runtime traces to CI artifacts or ignored output directories.
- Require final release evidence to be generated from a clean checkout.

#### Acceptance

- [ ] Verification leaves `git status` clean on an unchanged commit.
- [ ] Regeneration is deterministic or volatile fields are explicitly normalized.
- [ ] Current-state and release documents identify the assessed commit.
- [ ] CI preserves volatile evidence without committing routine churn.

**Evidence target:** `docs/release/ar_012_evidence_provenance_contract.md`

### AR-013: Add operational observability and rollback controls

**Goal:** prove that repaired privacy, billing, authentication, and compatibility flows can be operated safely after deployment.

#### Actions

- Add structured, privacy-safe audit events for POPIA operations, billing-provider interactions, auth lifecycle failures, and deprecated route use.
- Add 4xx/5xx, latency, failure, retry, and queue/job-state metrics where relevant.
- Define alert thresholds and on-call ownership for:
  - POPIA 5xx responses;
  - failed or stuck export/erasure jobs;
  - billing provider failures;
  - authentication error spikes;
  - deprecated alias usage after migration deadlines.
- Verify logs redact or omit tokens, personal payloads, decrypted email, export content, correction content, and erasure details.
- Document containment actions and feature-disable or rollback procedures.
- Rehearse rollback using the exact release candidate and prove data/migration compatibility.

#### Acceptance

- [ ] Repaired flows emit sufficient operational signals without sensitive payload leakage.
- [ ] Alerts are configured, tested, and owned.
- [ ] Deprecated alias usage can be measured and removal readiness assessed.
- [ ] Runbooks cover investigation, containment, and rollback.
- [ ] Rollback rehearsal succeeds against a disposable or approved staging environment.

**Evidence target:** `docs/operations/ar_013_observability_and_rollback_evidence.md`

### Phase 2 exit gate

- [ ] AR-006B, AR-008, AR-009, AR-012, and AR-013 are complete.
- [ ] Frontend env-check, lint, type-check, unit tests, and production build pass.
- [ ] Billing sends no fabricated customer identity.
- [ ] Test output contains no unresolved unawaited-coroutine or React state warnings.
- [ ] Release evidence is attributable and clean-checkout reproducible.
- [ ] Operational alerts and runbooks are tested.
- [ ] Rollback rehearsal succeeds.

---

## 12. Phase 3 — Authentication Maintainability

AR-011A through AR-011C are deliberately split so auth consolidation does not violate the small-reviewable-change rule.

### AR-011A: Define the canonical auth/token contract and characterization tests

#### Actions

- Name one canonical module for issuance, verification, refresh, revocation, key rotation, and claims.
- Define access and refresh token schemas including subject, role, token type, issuer, audience, expiry, and `kid` where applicable.
- Add characterization tests for current login, registration, refresh, protected-route, revocation, expiration, wrong-type, wrong-audience, and key-rotation behavior.
- Document migration boundaries before changing production callers.

#### Acceptance

- [ ] One written token contract is approved by Backend and Security.
- [ ] Characterization tests pass before migration begins.
- [ ] Access and refresh semantics are explicit and negative paths are covered.

### AR-011B: Migrate callers and isolate legacy auth behavior

#### Actions

- Migrate login, registration, refresh, and protected-route verification incrementally.
- Replace dynamic repository candidate resolution with explicit dependency injection where practical.
- Move compatibility behavior into a clearly named legacy namespace.
- Remove production monkey-patching dependencies in small PRs.

#### Acceptance

- [ ] Production callers use the canonical contract.
- [ ] Compatibility behavior is isolated and has a removal plan.
- [ ] Auth contract and route tests remain green after each migration PR.

### AR-011C: Remove retired auth paths and enforce boundaries

#### Actions

- Remove retired modules after consumers migrate.
- Add import-linter or equivalent checks blocking new imports of retired paths.
- Confirm documentation and tests reference the canonical implementation.

#### Acceptance

- [ ] Retired paths are removed or explicitly quarantined.
- [ ] Architecture checks prevent reintroduction.
- [ ] Runtime, security, and token contract tests pass.

**Combined evidence target:** `docs/security/ar_011_auth_consolidation_evidence.md`

### Phase 3 exit gate

- [ ] AR-011A through AR-011C are complete, or remaining P2 work has an approved deferral that does not undermine P0/P1 correctness.
- [ ] Canonical auth/token tests pass.
- [ ] No production auth behavior depends on undocumented monkey patches.
- [ ] Architecture checks prevent new use of retired paths.

---

## 13. Residual-Defect Register Requirements

The register created in AR-000 must contain at least:

| Field | Description |
| --- | --- |
| Defect ID | Stable identifier |
| Source AR | Workstream that exposed the issue |
| Failing command/test | Exact reproducible selector |
| Expected test count | Guard against accidental under-selection |
| Severity | Critical, High, Medium, Low |
| Release blocking | Yes/No, with rationale |
| DRI | One accountable individual |
| Approver | Person accepting closure or exception |
| Target milestone/date | Delivery commitment |
| Root cause | Updated as investigation proceeds |
| Fix PR | Link when available |
| Evidence | Passing command or approved exception |

A defect register is a visibility mechanism, not a substitute for passing P0 gates.

---

## 14. Pull Request Plan

Recommended sequence:

1. AR-000 baseline, DRI assignment, status metadata, and residual-defect register.
2. AR-001A registry tracking, `.gitignore` precision, and preflight.
3. AR-001B artifact classification and bootstrap command.
4. AR-001B focused Content Factory defect fixes.
5. AR-002 actor adapter and service migration.
6. AR-002 real-route POPIA regression tests and marker-count guard.
7. AR-003 frontend routes, parent actions, alias policy, and telemetry.
8. AR-004 duplicate-job cleanup and pnpm conversion.
9. AR-004 duplicate-key-aware workflow validator, `actionlint`, and Playwright ownership.
10. AR-005 OpenAPI regeneration and full operation-contract test.
11. AR-006A production API configuration enforcement.
12. AR-007 dependency-scan enforcement and controlled policy fixture.
13. AR-010 canonical environment identity and access proof.
14. AR-006B frontend lint and portable env-check cleanup.
15. AR-008 Stripe customer identity correction and provider telemetry.
16. AR-009 backend warning cleanup.
17. AR-009 frontend warning cleanup.
18. AR-012 evidence provenance contract.
19. AR-013 observability, alerts, runbooks, and rollback rehearsal.
20. AR-011A token contract and characterization tests.
21. AR-011B incremental auth caller migration.
22. AR-011C legacy removal and architecture enforcement.
23. AR-014 final evidence assembly and GO/NO-GO decision.

Every PR must include:

- linked AR and residual-defect IDs;
- problem and risk statement;
- implementation summary;
- tests added or changed;
- expected and actual test count;
- exact commands and exit results;
- migration, deployment, and rollback notes;
- security and privacy impact;
- observability impact;
- evidence paths updated;
- DRI and approver.

---

## 15. Dependency Order And Parallel Lanes

```text
AR-000
  -> AR-001A -> AR-001B
  -> AR-002 -> AR-003 -> AR-005
  -> AR-004 -> AR-006A -> AR-006B
            -> AR-007
            -> AR-010
  -> AR-012

AR-002 -> AR-008
AR-001B + AR-002 + AR-006B -> AR-009
AR-002 + AR-003 + AR-008 + AR-010 -> AR-013
AR-002 + AR-005 -> AR-011A -> AR-011B -> AR-011C

All non-waivable gates + all P0 + required P1/P2 disposition -> AR-014
```

Parallel lanes:

- **Content/backend:** AR-001A, AR-001B.
- **Privacy/API:** AR-002, AR-003, AR-005.
- **Platform/security:** AR-004, AR-007, AR-010.
- **Frontend:** AR-003, AR-006A, AR-006B, frontend portion of AR-009.
- **Billing/operations:** AR-008, AR-013.
- **Architecture:** AR-011A through AR-011C.
- **Release engineering:** AR-000, AR-012, AR-014.

---

## 16. Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Restored registry is stale relative to untracked external data | Curriculum behavior may not match recent local work | Treat restored files as last tracked policy, require Content review, record hashes, and prohibit silent count changes. |
| Artifact bootstrap reveals more missing inputs | Scope and schedule expand | Classify every artifact, create owned defects, and keep failures visible. |
| Broad fast tests expose unrelated failures | Phase 1 takes longer | Use the residual-defect register, but do not treat ownership as a passing gate. |
| Route aliases hide continuing drift | Privacy workflows stay brittle | Prefer canonical client migration; require deprecation, telemetry, and removal dates for aliases. |
| CI repair exposes suppressed failures | More blockers become visible | Do not restore suppression; prioritize by severity and release impact. |
| OpenAPI client checks validate only paths | Method/schema/auth drift persists | Validate full operation contracts. |
| Scanner-policy test pollutes lockfiles | Production dependencies are altered for testing | Use a controlled fixture or dedicated test project. |
| Auth consolidation breaks sessions | User access or security regresses | Characterize behavior first and migrate incrementally. |
| Canonical environment differs from source checkout | False readiness decision | Require commit, image, migration, OpenAPI, and registry identity evidence. |
| Logs leak personal information | Privacy or security incident | Use allow-listed structured fields and automated redaction tests. |
| Rollback is migration-incompatible | Failed release cannot be safely contained | Rehearse rollback and document forward-fix limits before GO. |
| Evidence continues to churn | Reviewers cannot trust provenance | Separate source and volatile artifacts; require clean-checkout verification. |

---

## 17. Strengths To Preserve

- Canonical and legacy FastAPI entrypoints import successfully.
- Alembic has a single head and migration/schema checks pass.
- Release-blocking Python syntax and name checks pass.
- Import-boundary contracts pass.
- Environment security and privacy-boundary checks pass.
- Admin Content Factory routes remain admin protected.
- Learner, diagnostic, lesson, and consent routes retain object-level authorization and consent controls.
- Security headers and production secret checks remain enforced.
- Frontend TypeScript and Vitest suites remain green.

Any remediation that regresses one of these controls requires its own defect and blocks closure until restored.

---

## 18. Full Release-Candidate Verification Matrix

Run from a clean checkout of the exact release commit. All commands must record exit code, duration, environment identity, and relevant test counts.

### 18.1 Source identity and cleanliness

```bash
git status --porcelain=v1
test -z "$(git status --porcelain=v1)"
git rev-parse HEAD
git branch --show-current
git remote -v
```

### 18.2 Backend static and architecture gates

```bash
.venv/bin/python -m compileall -q app scripts
.venv/bin/ruff check app tests scripts --select E9,F63,F7,F82,F821
.venv/bin/lint-imports
.venv/bin/python scripts/check_runtime_entrypoints.py
make content-factory-preflight
make test-fast
```

### 18.3 Database and migration verification

Use a disposable database created specifically for the release run. Never point this command at an unspecified developer, staging, or production database.

```bash
export RELEASE_TEST_DATABASE_URL='postgresql+psycopg://.../eduboost_release_test_<unique_id>'
DATABASE_URL="$RELEASE_TEST_DATABASE_URL" .venv/bin/python scripts/verify_migration_graph.py
DATABASE_URL="$RELEASE_TEST_DATABASE_URL" .venv/bin/python scripts/validate_schema_integrity.py
DATABASE_URL="$RELEASE_TEST_DATABASE_URL" .venv/bin/alembic heads
DATABASE_URL="$RELEASE_TEST_DATABASE_URL" .venv/bin/alembic upgrade head
```

Where downgrade is supported by policy, also test the approved rollback boundary against the disposable database. Do not assume every migration is safely reversible.

### 18.4 API and client contract

```bash
.venv/bin/python scripts/generate_openapi.py --check
corepack pnpm --dir app/frontend run api-contract-check
```

### 18.5 Frontend

```bash
corepack enable
corepack pnpm --dir app/frontend install --frozen-lockfile
corepack pnpm --dir app/frontend run env-check
corepack pnpm --dir app/frontend run lint
corepack pnpm --dir app/frontend run type-check
corepack pnpm --dir app/frontend run test -- --run
corepack pnpm --dir app/frontend run build
```

### 18.6 Workflow validation

```bash
actionlint
.venv/bin/python scripts/validate_github_workflows.py
```

### 18.7 Integration and container verification

```bash
make test-integration

docker compose config
docker compose -f docker-compose.prod.yml config

docker compose build --pull
docker compose up -d
.venv/bin/python scripts/wait_for_services.py --compose-project eduboost --timeout 180
.venv/bin/python scripts/verify_runtime_health.py --base-url http://localhost:<documented-port>
docker compose down -v --remove-orphans
```

If `wait_for_services.py` or `verify_runtime_health.py` does not exist, AR-013 includes adding equivalent deterministic checks. Configuration parsing alone is not sufficient container evidence.

### 18.8 Playwright E2E

Use the package directory selected in AR-004. Preferred form when `app/frontend` owns Playwright:

```bash
corepack pnpm --dir app/frontend exec playwright install --with-deps
corepack pnpm --dir app/frontend exec playwright test
```

The E2E gate must report the expected spec and test counts and fail when none are selected.

### 18.9 Security and privacy

Required release evidence includes:

- dependency scan at the approved blocking threshold;
- controlled scanner-policy fixture result;
- secrets scan;
- POPIA real-route suite and minimum-count assertion;
- environment security contract;
- privacy-boundary evidence check;
- Stripe billing identity tests;
- security-header tests;
- production frontend environment tests;
- log-redaction tests;
- deprecated-route telemetry check.

### 18.10 Observability and rollback

Required:

- alert test results;
- sample privacy-safe structured events;
- runbook review approval;
- rollback rehearsal result;
- confirmation that the rollback target and data/migration state are compatible.

---

## 19. AR-014 Dependencies And GO/NO-GO Rules

AR-014 does **not** simply depend on every numbered item being complete. It depends on the following precise state:

1. Every non-waivable gate is green.
2. Every P0 workstream is complete.
3. Every P1 workstream is complete or has a permitted, approved, unexpired exception.
4. Every P2 workstream is complete or has an approved deferral that does not undermine P0/P1 correctness, evidence, security, privacy, or operability.
5. The exact release commit passes CI and staging verification.
6. Final evidence is generated from a clean checkout and references the same commit and image deployed to staging.

### Controlled-beta GO criteria

GO may be considered only when:

- [ ] all non-waivable gates are green;
- [ ] all P0 workstreams are complete;
- [ ] all P1 workstreams are complete or covered by permitted, unexpired exceptions;
- [ ] all P2 workstreams are complete or formally deferred without undermining release correctness;
- [ ] `make test-fast`, required integration tests, and E2E tests pass with expected test counts;
- [ ] CI is green on the exact release commit;
- [ ] staging identity matches the release commit, image, migration head, OpenAPI hash, and registry hashes;
- [ ] POPIA export, erasure, cancellation, correction, and restriction work end to end;
- [ ] frontend, backend, OpenAPI, and E2E operation contracts agree;
- [ ] production frontend configuration points only to the intended backend;
- [ ] no critical/high unaccepted production vulnerability remains;
- [ ] billing sends no fabricated customer identity;
- [ ] privacy-safe observability and alerts are active;
- [ ] rollback has been rehearsed successfully;
- [ ] legal, content, security, privacy, operations, and release approvals are current.

Any failed criterion keeps the decision at **NO-GO**.

### Release decision record

The final decision must record:

- decision and timestamp;
- exact commit and image digest;
- staging environment identity;
- migration head;
- OpenAPI and registry hashes;
- CI run and evidence package links;
- approved exceptions and expiries;
- approvers;
- rollback target and owner.

**Evidence target:** `docs/release/ar_014_controlled_beta_decision.md`

---

## 20. Definition Of Done

This roadmap is complete when:

- [ ] every workstream has a final status, DRI, approver, and evidence link;
- [ ] all non-waivable gates are green;
- [ ] all required verification commands pass on the exact release commit;
- [ ] a clean checkout can build, test, generate contracts, and access or bootstrap every required Content Factory input;
- [ ] POPIA data-rights flows work end to end with real authentication dependencies;
- [ ] frontend, backend, OpenAPI, and E2E operation contracts agree;
- [ ] CI uses declared package managers, valid lockfiles, and duplicate-key-aware workflow validation;
- [ ] dependency and secrets scans enforce policy;
- [ ] billing sends no fabricated identity data;
- [ ] production builds fail closed on missing or unsafe API configuration;
- [ ] test suites have no unresolved async or React state warnings;
- [ ] operational logs and metrics are privacy safe;
- [ ] alerts, runbooks, and rollback are verified;
- [ ] generated evidence is attributable to a clean commit and reproducible;
- [ ] canonical staging identity and acceptance evidence are attached;
- [ ] the final release approver records a controlled-beta GO or NO-GO decision.

---

## 21. Immediate Next Actions

1. Complete AR-000: assign DRIs, approvers, calendar targets, source SHA, and evidence paths.
2. Verify the recorded registry restoration on the identified branch and commit.
3. Implement AR-001A preflight and AR-001B artifact classification before changing failing Content Factory expectations.
4. Start AR-002 and AR-004 in parallel.
5. Do not regenerate final OpenAPI until POPIA actor and route contracts are settled.
6. Do not claim release readiness until the exact-commit CI, canonical-environment identity, dependency policy, observability, and rollback gates all pass.
