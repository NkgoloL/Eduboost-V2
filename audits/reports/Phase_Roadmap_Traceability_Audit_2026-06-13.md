# Phase Roadmap Traceability Audit - 2026-06-13

## Scope

This audit compares the recent 13-phase roadmap documents against the live local WSL repository state:

1. Source of truth TODO: `docs/todos/todo.md`.
2. Phase execution plans: `docs/roadmap/execution/phase_N_execution_plan.md`.
3. Claimed completion reports: `docs/roadmap/execution/phase_N_implementation_report.md`.
4. Actual evidence: tracked files, current source/config, targeted test runs, and process artifacts.

The audit was run against the local WSL working tree at `master` with `git status --short --branch` initially clean: `## master...origin/master`.

Remote VM state was not used. GitHub Actions and staging were not live-verified in this audit; where CI/staging proof is required, absence of a current run URL or captured output is treated as unresolved.

## 2026-06-13 Remediation Addendum

After the initial audit identified missing process artifacts, the missing phase documents were backfilled as traceability artifacts. This repairs the document set required by `docs/roadmap/PROCESS_DISCIPLINE.md`; it does not convert unverified or failing phase work into completed implementation.

Current artifact verification after remediation:

| Phase | Execution plan | Implementation report | Release evidence | Implementation audit |
|---:|---|---|---|---|
| 1 | present | present | present | present |
| 2 | present | present | present | present |
| 3 | present | present | present | present |
| 4 | present | present | present | present |
| 5 | present | present | present | present |
| 6 | present | present | present | present |
| 7 | present | present | present | present |
| 8 | present | present | present | present |
| 9 | present | present | present | present |
| 10 | present | present | present | present |
| 11 | present | present | present | present |
| 12 | present | present | present | present |
| 13 | present | present | present | present |

## Verdict Definitions

- **Supported**: the plan, report, and current repo evidence agree, and current verification passes.
- **Mostly supported**: implementation is substantially present, but process evidence or a secondary acceptance item is incomplete.
- **Partial**: some artifacts/code exist, but the implementation does not satisfy the original phase acceptance criteria.
- **Overstated**: the implementation report marks the phase complete while current evidence contradicts key acceptance criteria.
- **Not auditable**: mandatory plan/report/evidence artifacts are missing enough that the phase cannot be independently traced.

## Executive Findings

### 1. Phase process discipline was not followed consistently

`docs/roadmap/PROCESS_DISCIPLINE.md` says every phase requires a `phase_N_execution_plan.md`, `phase_N_implementation_report.md`, release evidence, and an audit step before close. At the time of the initial audit, the artifact inventory was incomplete:

| Phase | Execution plan | Implementation report | Release evidence | Implementation audit |
|---:|---|---|---|---|
| 1 | missing | missing | present | missing |
| 2 | present | present | present | missing |
| 3 | present | missing | present | missing |
| 4 | missing | missing | missing | missing |
| 5 | present | present | present | present |
| 6 | present | present | present | present |
| 7 | present | present | present | missing |
| 8 | present | present | missing | missing |
| 9 | present | present | missing | missing |
| 10 | present | present | missing | missing |
| 11 | present | present | missing | missing |
| 12 | present | present | missing | missing |
| 13 | present | present | missing | missing |

Phases 5 and 6 were the only phases with the full plan/report/evidence/audit set before remediation. The missing documents have now been backfilled, with retrospective/process-debt language where applicable.

### 2. The live tracker still says the product is not beta-ready or production-ready

`docs/todos/todo.md` says the project is not public-beta-ready and not production-launch-ready. It keeps CI, frontend/browser proof, POPIA sweep, content/product readiness, staging, telemetry, legal, security, and beta tasks open. It also says not to mark tasks complete from implementation intent or documentation-only confidence.

That rule conflicts with several later phase reports, especially phases 8, 9, 12, and 13, which mark broad work complete without current release evidence files or live CI/staging proof.

### 3. Current verification supports some core backend claims

These current checks passed during the audit:

```text
.venv/bin/python -m compileall -q app scripts
.venv/bin/ruff check app tests scripts --select E9,F63,F7,F82,F821
.venv/bin/lint-imports
.venv/bin/python scripts/verify_migration_graph.py
.venv/bin/python scripts/validate_schema_integrity.py
.venv/bin/python scripts/check_runtime_entrypoints.py
.venv/bin/python scripts/check_environment_security_contract.py
.venv/bin/python scripts/check_privacy_boundary_evidence.py
.venv/bin/python scripts/check_arq_worker_import.py
.venv/bin/python -m pytest -q tests/unit/test_phase6_durable_jobs.py --no-cov
```

Important current failures:

```text
.venv/bin/python scripts/generate_openapi.py --check
# FAIL: OpenAPI drift detected

cd app/frontend && npm run lint
# FAIL: next lint --no-cache -> unknown option '--no-cache'

cd app/frontend && npm run env-check
# FAIL: python ../../scripts/validate_frontend_env.py -> python: not found

.venv/bin/python -m pytest -q tests/unit/test_content_scope_registry.py tests/unit/test_content_staging_seed_executor.py --no-cov
# FAIL: test_content_staging_seed_executor.py::test_valid_approved_artifact_creates_seed_item
```

## Phase-by-Phase Traceability

| Phase | Plan intent | Claimed done | Actual evidence | Verdict |
|---:|---|---|---|---|
| 1 | Release-blocking correctness fixes. | Roadmap/TODO treat Phase 1 as complete; no execution/report files under `docs/roadmap/execution`. | Fatal Ruff/correctness gates currently pass, but phase traceability artifacts are missing. | Mostly supported, process incomplete. |
| 2 | Topic map approval, content generation config/execution, QA, DB import, smoke testing, beta preparation. | Implementation report is a data-ingestion pipeline report, not the same scope as the execution plan. | Topic maps and ingestion assets exist. No current evidence proves all 50 topic maps approved, 150 lessons generated, DB import, QA >=98 percent, or beta smoke. Content Factory slice currently has 1 failing test. | Overstated / scope mismatch. |
| 3 | Frontend build, type-check, dependency, and test health. | Execution plan marks complete; no implementation report. | `npm run type-check` and Vitest unit suite passed in audit, but `npm run lint` fails and `npm run env-check` fails. Some CI workflows still use `npm ci` and missing `package-lock.json` despite pnpm lockfile. | Partial. |
| 4 | Python runtime/version alignment. | Roadmap points to ADR-026; no execution/report/evidence files. | `.python-version` and Dockerfiles are 3.12.3, but later workflows use loose `3.12` in several places and one workflow label still says Python 3.11 while configuring 3.12.3. | Mostly supported, not strictly complete. |
| 5 | Migrations and schema management. | Report says complete locally. | Migration graph and schema integrity checks pass. Evidence and audit files exist. | Supported. |
| 6 | Durable background jobs through ARQ, worker wiring, restart survival. | Report says complete with live Docker evidence. | ARQ import check passes; Phase 6 unit tests pass; job code uses ARQ for critical routes while request-adjacent BackgroundTasks remain. Evidence and audit files exist. | Supported. |
| 7 | Deployment and security hardening. | Report/evidence say complete; audit explicitly deferred. | Environment security contract passes. Evidence exists, but no Phase 7 audit file; plan itself marks audit deferred and roadmap close item not fully checked. | Mostly supported, process incomplete. |
| 8 | Privacy and authorization completion, including POPIA/data-rights closure. | Report says complete and merged; says no production code changed, only tests/docs. | No release evidence/audit files. Current POPIA service takes `AuthContext` from `require_auth_context` but calls `.get`, causing `AttributeError: 'AuthContext' object has no attribute 'get'`. Some claimed boundary test files are missing. `scripts/check_phase2_authorization_evidence.py` fails because `app/api_v2_routers/ether.py` is missing. | Overstated. |
| 9 | Coverage, CI, evidence renewal, OpenAPI, single route prefix, dormant router cleanup. | Report says complete. | `generate_openapi.py --check` fails. Report references `docs/reference/openapi.json`, but the repo has `docs/openapi.json` and no `docs/reference/openapi.json`. `.github/workflows/ci-cd.yml` still defines `schema-drift` twice. `/v2` compatibility aliases remain. | Overstated. |
| 10 | Workspace hygiene and auditability: clean-checkout reproducibility, tracked-file scans, safe cleanup. | Report says complete, but reframes scope as product documentation and runbooks. | Some cleanup/hygiene scripts exist, but the implementation report does not directly prove the roadmap acceptance checks, and no Phase 10 release evidence exists. | Partial. |
| 11 | Technical debt burn-down: Ruff, import-linter, route comments, migration audit, dormant routers. | Report says complete for I.1/I.2/I.5 and deferred for I.3/I.4. | Import-linter passes, but `ruff check --statistics` still reports 645 findings; report's own definition of done target was <=100. Route comment and migration audit work is deferred. | Partial / self-reported incomplete. |
| 12 | Security posture: threat model, pen-test checklist, secrets scan, dependency scan, Dependabot gating. | Report says complete. | Docs/workflows exist, but dependency scan suppresses failures with `|| true`; vulnerability results become warnings, not blocking gates. Workflow also references `steps.publish.outputs.result_url` without a `publish` step. No Phase 12 release evidence exists. | Overstated. |
| 13 | Frontend/product completeness: Playwright, content roadmap, Locust, a11y/PWA, multilingual, Supabase ADR. | Report says complete. | Locust/docs/ADR files exist. Report later admits axe assertions are not added, E2E execution requires backend and was not blocking, PWA is unverified, and Afrikaans/isiXhosa are partial/basic. Current frontend lint/env-check fail. | Overstated. |

## Key Evidence Details

### Phase 2 content and registry evidence

The Content Factory registry history shows the registry was intentionally removed in housekeeping and then restored:

```text
d7a8f9b5 chore: restore audit remediation workspace state
  A data/content_factory/coverage_targets.json
  A data/content_factory/scopes.json
6b3c2196 chore: move generated data to WSL external storage, ignore IDE index files
  D data/content_factory/coverage_targets.json
  D data/content_factory/scopes.json
```

Current tracked data includes topic maps and registry files, but the content-generation acceptance claims are not proven:

- `data/caps/topic_maps/` contains many topic-map JSON files.
- `data/content_factory/scopes.json` and `data/content_factory/coverage_targets.json` are tracked again.
- No current audit evidence proved the Phase 2 plan's 50 approved maps, 150 generated lessons, QA >=98 percent, database import, and smoke testing.
- `tests/unit/test_content_staging_seed_executor.py::test_valid_approved_artifact_creates_seed_item` fails on the current code/test slice.

### Phase 3 and Phase 13 frontend evidence

Current frontend evidence is mixed:

- `npm run type-check` passed.
- `npm run test -- --run` passed: 147 tests across 43 files, with React `act(...)` warnings.
- `npm run lint` fails because `app/frontend/package.json` runs `next lint --no-cache`, and the installed Next CLI rejects that option.
- `npm run env-check` fails because the script calls `python`, but the WSL environment exposes `python3`/venv Python rather than `python`.
- `app/frontend/package.json` declares pnpm, and `app/frontend/pnpm-lock.yaml` exists.
- `app/frontend/package-lock.json`, root `package-lock.json`, and `docs/reference/openapi.json` do not exist.
- `.github/workflows/frontend-e2e.yml` and parts of `.github/workflows/ci-cd.yml` still use npm/package-lock paths.

### Phase 8 POPIA/data-rights evidence

`app/api_v2_routers/popia.py` injects `current_user` with `Depends(require_auth_context)`. `require_auth_context` returns an `AuthContext`. `app/services/popia_service.py` then calls `current_user.get(...)` in data export, erasure, correction, restriction, and execute-erasure flows.

Direct runtime proof:

```text
AttributeError: 'AuthContext' object has no attribute 'get'
```

This makes the Phase 8 "privacy and authorization completion" claim unsafe for POPIA data-rights runtime paths even though some static/wiring tests pass.

### Phase 9 CI/API contract evidence

Current API/CI drift:

- `scripts/generate_openapi.py --check` fails.
- Phase 9 report claims OpenAPI was committed at `docs/reference/openapi.json`; current tracked file is `docs/openapi.json`.
- `.github/workflows/ci-cd.yml` defines `schema-drift` at two separate job keys.
- Compatibility route aliases remain documented in `docs/release/route_alias_matrix.md`, while Phase 9 roadmap acceptance expected routes registered under exactly one prefix.

### Phase 11 technical debt evidence

The implementation report claims I.1 complete while also reporting a missed definition-of-done target. Current Ruff statistics still show 645 non-blocking findings:

```text
396 E402
137 E701
94  E702
10  E741
7   E712
1   F601
```

The report also defers route-comment hygiene and migration audit. Therefore Phase 11 is not actually closed against its own execution plan.

### Phase 12 security evidence

The dependency scan workflow exists, but it does not enforce the Phase 12 roadmap acceptance criterion that CI blocks on critical dependency vulnerabilities:

- `pip-audit ... > pip-audit.json || true`
- `pnpm audit --json > pnpm-audit.json || true`
- vulnerability findings emit warnings rather than failing the job
- SARIF upload references `steps.publish.outputs.result_url`, but there is no `publish` step in the job

The security posture improved through documentation/workflow scaffolding, but the "CI blocks on critical-severity dependency vulnerabilities" acceptance check is not met.

### Phase 13 product completeness evidence

Phase 13 created useful artifacts:

- `locust/locustfile.py`
- `locust/README.md`
- `docs/caps/content_expansion_roadmap.md`
- `docs/caps/multilingual_status.md`
- `docs/development/e2e_testing.md`
- `docs/development/pwa_offline_plan.md`
- `docs/adr/ADR-029-supabase-auth-strategy.md`

However, the implementation report contradicts its own completion claim:

- axe-core assertions are not added to tests
- E2E suite execution requires a backend and was not treated as blocking
- PWA state is documented as unverified
- Afrikaans and isiXhosa support are partial/basic and need review
- current frontend lint/env-check fail

The correct verdict is "planning/scaffolding delivered, product verification incomplete."

## TODO Alignment

The TODO file remains more honest than the later phase reports. It still keeps these areas open:

- CI green on master
- frontend/browser behavior proof
- POPIA sweep and sign-offs
- content/product readiness
- staging smoke and telemetry
- operational backup/restore/rollback proof
- beta readiness and real learner beta period
- branch protection and governance evidence

The TODO's completion rule says not to mark `[x]` based on implementation intent or documentation-only confidence. Several implementation reports violate that standard by marking documentation, plans, or unrun workflows as complete.

## Recommendations

1. Reopen phases 8, 9, 12, and 13 as incomplete until current executable evidence exists.
2. Treat phases 5 and 6 as the model for future closeout: plan, implementation report, release evidence, audit, and current passing commands.
3. Fix current release blockers before producing another completion report:
   - regenerate or intentionally update `docs/openapi.json`
   - fix frontend `lint` and `env-check` scripts
   - convert POPIA services from dict-style auth access to `AuthContext`-aware access
   - fix duplicate/mismatched CI jobs and npm/pnpm lockfile usage
   - make dependency scanning fail on agreed vulnerability thresholds
4. Update `docs/roadmap/README.md` to point to `docs/todos/todo.md`; it currently points to a missing root `TODO.md`.
5. Add missing release evidence files for phases 8-13 or downgrade the roadmap status to "partial/scaffolded."
6. For Phase 2, decide whether the phase is "content generation and beta content" or "ingestion pipeline"; the plan and report currently audit as different scopes.
7. Keep the Content Factory registry tracked, but do not treat restoration as full content readiness until staging seed/content generation tests pass.

## Bottom Line

The recent phase work did add real value, especially in migrations, durable jobs, security documentation, product documentation, and frontend/product scaffolding. The process-required document set is now present for all 13 phases. But the claim that all 13 phases are complete remains unsupported by the current repo. The defensible implementation status is:

- **Supported**: Phase 5, Phase 6.
- **Mostly supported but process-incomplete**: Phase 1, Phase 4, Phase 7.
- **Partial or overstated**: Phase 2, Phase 3, Phase 8, Phase 9, Phase 10, Phase 11, Phase 12, Phase 13.

The roadmap should be reconciled to the TODO, not the other way around.
