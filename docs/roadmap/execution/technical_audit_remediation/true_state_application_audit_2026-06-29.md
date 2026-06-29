# True State Application Audit - 2026-06-29

## Scope

This audit was performed from the live checkout, not from roadmap or closure
documentation. Documentation was treated as an artifact to verify, not as a
source of truth.

Repository state inspected:

- Branch: `codex/phase-06-e2e-playwright-authority`
- HEAD: `29d8f904c89194aa29e55b85c9c06794515c6cac`
- Remote branch: `origin/codex/phase-06-e2e-playwright-authority` at the same SHA
- Base branch observed: `origin/master` at `c2689a2e43a6d9cc2b149fa00d461d4a7837c789`
- Runtime tools: Python `3.12.3`, Node `v22.22.3`, pnpm `9.14.4`
- Worktree after cleanup: tracked files clean; untracked legacy diagnostics remain at `docs/release-evidence/technical-audit/hosted-ci-merge-readiness/`

Generated tracked changes produced by the audit run were preserved in
`stash@{0}` as `codex-audit-generated-artifacts-20260629`.

## Executive Verdict

The application is partially verified and usable in important local paths, but
the repository is not in a fully green authority state.

Verified live:

- FastAPI canonical and legacy entrypoints import successfully.
- OpenAPI generation is current.
- Frontend install, environment check, type-check, lint, and Vitest pass.
- Frontend production build passes.
- Mocked Playwright learner and parent E2E journeys pass.
- Phase 02R terminal gate control verifies.
- Technical-audit release-readiness and closure records verify.
- Most historical evidence bundles verify by checksum and manifest rules.

Not green:

- `make test-fast` fails on the current branch.
- The direct hosted CI authority verifier fails because the recorded run payload
  SHA does not match the authority record SHA.
- Several intermediate technical-audit verifier scripts still reject the final
  closed register state because they require old `active_slice` values.
- Local readiness endpoints are not healthy because Postgres and Redis are not
  running in this audit environment.

## Fresh Verification Results

### Git and Environment

Command:

```bash
git branch --show-current
git rev-parse HEAD
git status --short
python3 --version
.venv/bin/python --version
node --version
pnpm --version
```

Observed:

- Branch: `codex/phase-06-e2e-playwright-authority`
- HEAD: `29d8f904c89194aa29e55b85c9c06794515c6cac`
- Python: `3.12.3`
- Node: `v22.22.3`
- pnpm: `9.14.4`
- Only persistent untracked item after cleanup: `docs/release-evidence/technical-audit/hosted-ci-merge-readiness/`

### Backend Runtime Entrypoints

Command:

```bash
.venv/bin/python scripts/check_runtime_entrypoints.py --json
```

Result: passed.

- `app.api_v2:app`: loaded, title `EduBoost SA V2`, version `2.0.0`, route count `421`
- `app.legacy.api.main:app`: loaded, title `EduBoost SA V2`, version `2.0.0`, route count `422`
- Required canonical routes and `/api/v2` / `/v2` prefixes were present.

### Backend HTTP Probe

Probe used `fastapi.testclient.TestClient` against `app.api_v2:app`.

Results:

- `/`: `200`, JSON body includes `EduBoost SA V2`
- `/health`: `200`, status `ok`, version `2.0.0`, environment `development`
- `/openapi.json`: `200`
- `/api/v2/system/health`: `200`
- `/ready`: `503`, with Postgres and Redis connection failures
- `/v2/health/deep`: `503`, with Postgres and Redis connection failures

Interpretation:

The app imports and serves shallow health/API metadata locally, but full
readiness is not proven without running Postgres and Redis.

### OpenAPI Drift

Command:

```bash
.venv/bin/python scripts/generate_openapi.py --check
```

Result: passed with no drift output.

### Phase 02R Terminal Control

Command:

```bash
.venv/bin/python scripts/phase02r_gate_control.py \
  --expected-approved-gate 2R.8 \
  --expected-authorised-gate null \
  --require-approval-roles \
  --require-evidence-index-sha \
  --json
```

Result: `valid: true`, `errors: []`.

### Python Compile Check

Command:

```bash
.venv/bin/python -m compileall -q app scripts
```

Result: passed.

### Backend Fast Gate

Command:

```bash
make test-fast
```

Result: failed.

Pytest summary:

- `2367 passed`
- `11 skipped`
- `1 xfailed`
- `7 failed`
- `7 warnings`

Failing tests:

- `tests/unit/audit_remediation/test_backend_fast_phase02k.py::test_phase02k_verifier_assets_are_present`
- `tests/unit/audit_remediation/test_backend_fast_phase02l.py::test_phase02l_verifier_assets_are_present`
- `tests/unit/audit_remediation/test_backend_fast_phase02m.py::test_phase02m_verifier_assets_are_present`
- `tests/unit/audit_remediation/test_backend_fast_phase02m.py::test_historical_phase_verifiers_are_not_pinned_to_active_slice`
- `tests/unit/audit_remediation/test_technical_audit_baseline_contracts.py::test_dependency_scan_workflow_uses_pnpm_summary`
- `tests/unit/audit_remediation/test_dependency_scan_enforcement.py::test_dependency_scan_verifier_accepts_current_contract`
- `tests/unit/audit_remediation/test_e2e_playwright_authority.py::test_e2e_playwright_authority_verifier_passes`

Root pattern:

The failures are governance/verifier contract failures, not ordinary backend
business-logic failures. The failing scripts still require intermediate
`active_slice` values such as backend-fast Phase 02K/02L/02M, Phase 05, or
Phase 06. The live register now records a terminal closed state:
`technical-audit-remediation-closed`.

### Frontend Authority

Command:

```bash
.venv/bin/python scripts/audit_remediation/run_frontend_tooling_authority.py \
  --output-dir /tmp/eduboost-audit-frontend-authority \
  --json
```

Result: `valid: true`.

Steps passed:

- `pnpm --version`
- `pnpm --dir app/frontend install --frozen-lockfile`
- `pnpm --dir app/frontend run env-check`
- `pnpm --dir app/frontend run type-check`
- `pnpm --dir app/frontend run lint`
- `pnpm --dir app/frontend run test`

### Frontend Production Build

Command:

```bash
pnpm --dir app/frontend run build
```

Result: passed.

Observed:

- Next.js `16.2.7`
- Production build compiled successfully.
- TypeScript completed.
- Static generation completed for `24` pages.
- Service worker bundling completed.

### Mocked Playwright E2E Authority

Command:

```bash
.venv/bin/python scripts/audit_remediation/run_e2e_playwright_authority.py \
  --output-dir /tmp/eduboost-audit-e2e-authority \
  --json
```

Result: `valid: true`.

Steps passed:

- root pnpm install with frozen lockfile
- frontend pnpm install with frozen lockfile
- Playwright version check
- Chromium install/check
- mocked learner journey
- mocked parent journey

Boundary:

This proves mocked frontend journeys only. It does not prove full
backend-backed E2E readiness.

## Evidence and Governance Verification

### Evidence Bundles That Verify

The following current evidence verifiers returned `valid: true`:

- Backend fast gate evidence:
  `scripts/audit_remediation/verify_backend_fast_evidence.py`
- Frontend tooling authority evidence:
  `scripts/audit_remediation/verify_frontend_tooling_evidence.py`
- CI authority workflow evidence:
  `scripts/audit_remediation/verify_ci_authority_workflow_evidence.py`
- Dependency scan enforcement evidence:
  `scripts/audit_remediation/verify_dependency_scan_evidence.py`
- E2E Playwright authority evidence:
  `scripts/audit_remediation/verify_e2e_playwright_evidence.py`
- OpenAPI frontend contract evidence:
  `scripts/audit_remediation/verify_openapi_frontend_contract_evidence.py`
- Remote CI branch integration evidence:
  `scripts/audit_remediation/verify_remote_ci_branch_integration_evidence.py`
- Technical-audit merge readiness:
  `scripts/technical_audit/verify_merge_readiness_authority.py`
- Technical-audit release readiness:
  `scripts/technical_audit/verify_release_readiness_authority.py`
- Technical-audit closure:
  `scripts/technical_audit/verify_technical_audit_closure.py`

### Direct Verifiers That Fail In Current Terminal State

The following direct current-state verifiers failed:

- `scripts/audit_remediation/verify_backend_fast_phase02k.py`
  - Error: `blocker register active_slice must remain within the backend-fast 02-series remediation stream`
- `scripts/audit_remediation/verify_backend_fast_phase02l.py`
  - Error: `blocker register active_slice must remain within the backend-fast 02-series remediation stream`
- `scripts/audit_remediation/verify_backend_fast_phase02m.py`
  - Errors: expected `02m-backend-fast-head-aligned-finalization` and HEAD-aligned evidence policy
- `scripts/audit_remediation/verify_dependency_scan_workflow.py`
  - Error: `active_slice is technical-audit-remediation-closed`
- `scripts/audit_remediation/verify_dependency_scan_enforcement.py`
  - Error: `active_slice is technical-audit-remediation-closed`
- `scripts/audit_remediation/verify_e2e_playwright_authority.py`
  - Error: `Phase 06 active slice registered`
- `scripts/audit_remediation/verify_ci_authority_workflow.py`
  - Errors: missing exact `cache-dependency-path: app/frontend/pnpm-lock.yaml` snippet and `active_slice is technical-audit-remediation-closed`
- `scripts/audit_remediation/verify_remote_ci_branch_integration_authority.py`
  - Errors: expected Phase 08 active slice/status; also warns worktree is not clean because of the untracked legacy diagnostics directory

Interpretation:

The terminal closure state is incompatible with several historical phase
verifiers. Those scripts need terminal-state tolerance or archival semantics if
they are expected to remain part of `make test-fast`.

### Hosted CI Authority Mismatch

Command:

```bash
.venv/bin/python scripts/technical_audit/verify_hosted_ci_authority.py --json
```

Result: failed.

Error:

- `run view headSha does not match record head_sha`

Observed values:

- Current branch HEAD: `29d8f904c89194aa29e55b85c9c06794515c6cac`
- Hosted CI authority record `head_sha`: `d8b6c1c85a155c3927f48607b7c78c3ada44c28e`
- Raw GitHub run view `headSha`: `0892958b986bcb4a054e90a1bf4c72f6736db77a`
- Raw run ID: `28332718788`
- Raw run conclusion: `success`

Interpretation:

The record claims hosted CI success and merge readiness, but the strict hosted
CI verifier does not currently accept the evidence chain because the run view
payload SHA and record SHA differ. Later commits advanced the branch after the
CI run. This is the most important provenance issue found in the audit.

## Release Boundary State

Fresh verifier results show:

- Technical-audit remediation closure: valid
- Technical-audit release readiness: claimed
- Merge readiness: authorised
- Branch protection: claimed
- Production release: not authorised
- Deployment: not authorised
- Release tag: not authorised
- Live learner traffic: not authorised
- Runtime KG implementation: not claimed

Important nuance:

The closure verifier passes, but the hosted CI verifier does not. Therefore the
strongest true statement is: technical-audit closure artifacts validate under
their closure verifier, but hosted CI provenance is not fully consistent under
the direct hosted CI authority verifier.

## Main Findings

### P0 - Backend Fast Gate Is Red On Current HEAD

`make test-fast` fails with 7 test failures. Because this is the declared fast
backend authority gate, the current branch should not be described as fully
green.

Recommended fix:

Update historical technical-audit verifier scripts and their tests so completed
terminal state is accepted where appropriate, while still rejecting stale active
intermediate slices during those phases.

### P0 - Hosted CI Authority Provenance Is Inconsistent

The raw hosted CI run succeeded, but its `headSha` does not match the authority
record `head_sha`, and neither matches the current branch HEAD.

Recommended fix:

Recapture hosted CI evidence from a successful run whose `headSha` equals the
current branch HEAD, or revise the authority model to record distinct CI-run
SHA, evidence commit SHA, and terminal closure SHA.

### P1 - Terminal Register State Breaks Historical Verifiers

Several remediation verifiers assume their phase is the current active slice.
That is no longer true after closure.

Recommended fix:

Split verifier intent into:

- phase-local verifier: validates the active slice while that phase is open
- archival verifier: validates recorded evidence after the stream is closed
- terminal verifier: validates the final closure state

### P1 - Local Readiness Is Not Proven

The app imports and shallow health works, but `/ready` and `/v2/health/deep`
return `503` because Postgres and Redis are unavailable in this local audit
run.

Recommended fix:

Run a live stack readiness audit with Postgres and Redis up, then rerun
readiness probes and integration tests.

### P2 - Untracked Legacy Diagnostics Directory Remains

The directory `docs/release-evidence/technical-audit/hosted-ci-merge-readiness/`
is still untracked. Previous workflow notes indicate it was intentionally left
uncommitted, but it still causes clean-tree-sensitive verifiers to report an
unclean worktree.

Recommended fix:

Either archive it outside the repo, add it to an explicit ignored diagnostics
path, or commit it deliberately if it is still needed.

## Overall Assessment

The application code is not collapsed or non-runnable: backend imports,
OpenAPI, frontend build, frontend tests, and mocked E2E journeys all work from
the live checkout. The biggest risks are in the control plane around evidence
freshness and terminal-state verifier compatibility.

Do not claim a fully green current HEAD until:

1. `make test-fast` passes.
2. Hosted CI authority evidence is refreshed or semantically repaired.
3. Historical phase verifiers are made terminal-state aware.
4. Local or controlled environment readiness is proven with Postgres and Redis.

