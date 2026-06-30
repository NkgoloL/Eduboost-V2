# EduBoost V2 Technical Audit

Date: 2026-06-02  
Audited path: `azureuser@135.119.52.214:/home/azureuser/Dev/Eduboost-V2`  
Audit stance: implementation-first. Documentation was treated as context only after inspecting code, config, tests, and executable checks.

## Executive Assessment

The project is a substantial FastAPI plus Next.js codebase with serious backend architecture work, broad test inventory, POPIA/consent concepts, observability assets, and a verified Grade 4 Mathematics launch-content slice. It is not currently in a clean production-ready state.

The backend can import and a small smoke subset passes, but full static health is poor: Ruff reports 861 findings, `compileall` finds a real syntax error in a maintenance script, the stored backend coverage artifact reports only 40.9 percent line coverage, and the Python runtime story is inconsistent.

The frontend is currently not healthy from the checked-out runtime: TypeScript fails, `dexie` is declared and locked but not resolvable from installed `node_modules`, and Vitest fails 15 suites due JSX/TSX parse failures. This is a concrete build/test blocker, not a documentation mismatch.

Security and privacy controls are partially real: most learner-sensitive routes have auth, object authorization, and active-consent checks; admin Content Factory routes are protected; JWT revocation and production placeholder-secret checks exist. However, route introspection found non-public-looking routes without auth, most notably practice session continuation endpoints, and several production/deployment surfaces are inconsistent.

The repo carries a lot of ignored local/build state: `.venv`, frontend `node_modules`, frontend `.next`, coverage HTML, caches, and pyc files. Git is clean, but the working directory is operationally bulky and can mislead file inventory and scanner results.

## Evidence Snapshot

Git state:

- Branch: `master`, tracking `origin/master`.
- Commit: `241e7ebff5384db2d9135539f52b9cb888338c6e`.
- Latest commit observed: `241e7ebf 2026-06-02 15:38:40 +0200 NkgoloL Merge pull request #194 from NkgoloL/remediation/phase0-phase1`.
- `git status --porcelain=v1 -b` was clean before and after the audit commands.

Repository shape:

- Raw working directory: 2.3 GB, 79,383 files, 9,568 directories.
- Tracked files: 3,913.
- Tracked area counts: `app` 576, `tests` 744, `app/frontend/src` 206, `scripts` 648, `docs` 1,489, `audits` 99.
- Major ignored local state: `.venv` 972 MB, `app/frontend` 1.1 GB mostly from `node_modules` and `.next`, `coverage_html` 21 MB.
- Generated/install artifacts are ignored and not tracked: `git ls-files app/frontend/node_modules app/frontend/.next .venv coverage_html .coverage coverage.xml .pytest_cache .ruff_cache` returned 0.

Runtime versions:

- `.python-version`: 3.12.3.
- Remote `.venv`: Python 3.11.0rc1.
- Dockerfiles: `python:3.11-slim`.
- GitHub Actions mostly use Python 3.12.3.
- Requirements files are generated with Python 3.12 metadata.
- Node observed: 20.20.2.
- Frontend `packageManager`: `pnpm@9.14.4`; a root shell check also showed a global pnpm 10.34.1, so package-manager invocation context matters.

## Backend Runtime State

Actual FastAPI entrypoint:

- Active app: `app/api_v2.py`.
- Import under test settings succeeded.
- Imported app exposes 355 routes.
- The app registers nearly all routers twice, under both `/api/v2` and `/v2`.
- Operational public routes include `/health`, `/ready`, `/api/v2/health/deep`, `/v2/health/deep`, `/metrics`, docs, and root.
- Dormant or not-main-entrypoint router files exist, including `app/api_v2_routers/api_v2.py`, `ether.py`, `judiciary.py`, `test_api.py`, `test_services.py`, and `0005_irt_seed.py`. These are not all registered by `app/api_v2.py`.

Backend positives:

- JWT signing uses a keyring layer and production placeholder-secret guard.
- Token revocation checks exist for JTI and user-level revocation.
- Global exception handlers wrap HTTP, validation, JWT, integrity, rate-limit, and unknown errors in the API envelope.
- Request ID, structured logging, timing, Prometheus metrics, and security headers are registered.
- Readiness checks cover required secrets, PostgreSQL, Redis, migrations, audit repository, LLM provider, and judiciary safety.
- Admin Content Factory and Admin ETL routers declare `Depends(require_admin)` at router level.
- Most learner-data route families explicitly call object authorization and active-consent helpers.

Backend risks and gaps:

- `app/api_v2.py` performs production startup schema repair outside Alembic. This is an operational smell: production schema mutation belongs in migrations or a controlled migration job, not arbitrary app startup.
- `/metrics` is unauthenticated. That may be acceptable behind private networking, but it is exposed by the app itself.
- `/__dev/slow_query` is unauthenticated in non-production. It hides in production, but should still be constrained in shared staging/dev environments.
- Security headers include a permissive CSP with `script-src 'self' 'unsafe-inline'` and `style-src 'self' 'unsafe-inline'`.
- `SecurityHeadersMiddleware` sets HSTS unconditionally, including development HTTP contexts.
- Some route comments still say "trust the lesson_id is known only to the authorized user," although the current implementation now calls authorization helpers. Comments lag behavior and can mislead reviewers.

## Route Authorization Findings

FastAPI route dependency introspection found:

- Total routes: 355.
- Routes protected by auth/admin dependency: 312.
- Routes without auth dependency: 43.
- Non-public-looking no-auth routes after excluding docs/health/root and core auth bootstrap: 25, mainly duplicated under `/api/v2` and `/v2`.

No-auth routes that deserve review:

- `GET /api/v2/practice/sessions/{session_id}/next-item`
- `POST /api/v2/practice/sessions/{session_id}/respond`
- The same two under `/v2`.
- `GET /api/v2/lessons/coverage` and `/v2/lessons/coverage`
- `GET /api/v2/gamification/leaderboard` and `/v2/gamification/leaderboard`
- `GET /api/v2/system/*` and `/v2/system/*`
- `GET /__dev/slow_query`

Practice session issue:

- `POST /practice/sessions` is protected and enforces learner write plus active consent.
- Follow-up routes use only `_SESSIONS[session_id]`, an in-memory dict.
- `next-item` and `respond` do not require auth, do not bind the session to the current user, and do not re-check consent.
- Any caller with a session id can read/advance that practice session in the running process.
- Sessions are not durable across restarts or multiple workers.

Expected public routes:

- `forgot-password`, `reset-password`, and `verify-email` are public by design and token based.
- Stripe webhook is public by design, but signature verification exists in `app/core/stripe_client.py`.

## Persistence and Migrations

Observed migration state:

- 31 Alembic migration files.
- Single script head: `20260528_1700`.
- Migration graph declarations appear resolvable.
- `alembic current --verbose` failed because `DATABASE_URL` was not exported, even though `alembic.ini` contains a URL. `alembic/env.py` intentionally refuses to use the ini URL.

Risks:

- Local migration commands are not self-contained; they require environment setup.
- Runtime startup repair in `app/api_v2.py` overlaps with Alembic responsibility.
- Docker container startup does not run `alembic upgrade head`; it relies on external migration handling plus startup repair.
- The app's `create_all_tables()` dev/test helper creates schema and applies audit immutability rules, but that is not a substitute for migration verification.

ORM inventory:

- Core models include guardians, learner profiles, parental consents, consent history, erasure requests, audit events/logs, IRT/diagnostic/session/mastery/lesson tables, Stripe events, auth extension tables, item exposure, and Content Factory tables.
- `StudyPlan` table class lives in `app/repositories/study_plan_repository.py`, not `app/models`, which is unusual and easy to miss in model import/autogenerate workflows.

## Jobs and Durability

Actual queued API behavior:

- `app/core/jobs.py` uses FastAPI `BackgroundTasks`.
- Job status is written to Redis when available and to an in-process `_MEMORY_JOBS` dict.
- This is not durable job execution: if the API process restarts after returning `202`, the handler is lost.
- Lesson generation, study-plan generation, and admin-triggered consent renewal currently enqueue through this request-adjacent background task layer.

ARQ state:

- `app/modules/jobs.py` defines ARQ worker settings and jobs for consent renewal, RLHF batch export, stale diagnostic expiry, and database backup.
- I did not find deployment wiring for an ARQ worker in `docker-compose.yml`, `docker-compose.prod.yml`, Dockerfiles, or workflow grep.
- `app/modules/jobs.py` appears to reference lowercase settings attributes (`cfg.redis_url`, `cfg.sendgrid_api_key`, `cfg.sendgrid_from_email`) while `Settings` defines uppercase names (`REDIS_URL`, `SENDGRID_API_KEY`, etc.). If that path is executed as-is, it likely raises `AttributeError`.
- `process_rlhf_feedback_batch` is still a placeholder that returns `exported` without implementing storage export.

## Frontend State

Stack:

- Next.js 15.5.18.
- React 18.3.1.
- TypeScript 5.4.5.
- Vitest 4.1.7.
- pnpm lock exists.
- `app/frontend/.env.production` is tracked; redacted inspection showed only `NEXT_PUBLIC_*` keys.

Fresh checks:

- `pnpm exec tsc --noEmit --pretty false` failed.
- Errors included missing `dexie` module and implicit `any` parameters in `src/lib/db/cache-api.ts` and `src/lib/db/storage-budget.ts`.
- `dexie` is declared in `package.json` and locked in `pnpm-lock.yaml`, but `node -e "require.resolve('dexie')"` failed. Installed `node_modules` does not match the manifest.
- `pnpm exec vitest run --reporter=dot` failed: 15 suites failed, 28 suites passed, and 104 tests passed before suite failures.
- Vitest suite failures are parse failures around JSX in `.tsx` tests. The output references Rolldown/Vite parse failures such as `Unexpected JSX expression`.
- `tsconfig.json` uses `"jsx": "preserve"`. With the current Vitest/Vite/Rolldown toolchain, that appears to be part of the TSX parsing problem.
- I did not run `pnpm install` because it would modify remote `node_modules` during an audit.

Frontend deployment concerns:

- `next.config.js` defaults API rewrites to `https://eduboost-api.onrender.com/api/v2` when `NEXT_PUBLIC_API_URL` is empty.
- Production Compose sets `NEXT_PUBLIC_API_URL` default to `/api/v2`.
- The root `package.json` is not the frontend manifest; the real frontend manifest is `app/frontend/package.json`.

## Static Quality and Test Results

Fresh executable checks:

- FastAPI import and route introspection: passed under test env.
- `pytest --collect-only --no-cov -q`: 3,345 tests collected in 36.48s.
- Targeted backend smoke: 34 passed, 3 skipped in 5.34s.
- `lint-imports --config .importlinter`: 3 contracts kept, 0 broken.
- `python -m compileall -q app scripts`: failed.
- `ruff check app tests scripts --output-format concise`: failed with 861 findings.
- `pnpm exec tsc --noEmit --pretty false`: failed with 8 TypeScript errors.
- `pnpm exec vitest run --reporter=dot`: failed, 15 failed suites, 28 passed suites.
- Existing `.coverage` and `coverage.xml` artifacts from earlier on 2026-06-02 report 40.9 percent total backend coverage. This is below the CI threshold of 67 and should be treated as stale evidence unless regenerated.

Concrete syntax error:

- `scripts/maintenance/audit_todo_backlog.py:347`
- Failure: `SyntaxError: f-string expression part cannot include a backslash`
- Cause: inline `.replace('|','\\|')` inside an f-string expression.

Ruff state:

- 861 findings across app, scripts, and tests.
- Categories include unused imports, module-level imports after code, redefinitions, ambiguous variable names, multiple statements on one line, local variables assigned but unused, and one notable undefined name:
  - `app/services/etl/etl_pipeline_v2.py:566:41: F821 Undefined name f`

CI gate mismatch:

- The main CI Ruff gate uses `ruff check app/ tests/ --select E9,F63,F7,F82`, so it catches only a narrow class of correctness errors.
- Mypy is `continue-on-error`.
- Several quality steps are also `continue-on-error`.
- This explains how the repo can carry 861 Ruff findings while still relying on CI as a partial gate.

## Content and Curriculum Data

Launch content validation was run directly:

- Command: `python scripts/validate_launch_content.py --strict`
- Status: ok.
- Approved item counts: `4.M.1.1` 40, `4.M.1.2` 40, `4.M.1.3` 40.
- Approved lesson counts: `4.M.1.1` 8, `4.M.1.2` 8, `4.M.1.3` 8.
- Blueprints: 10.

Data files exist under:

- `data/caps/grade4_maths_item_bank.json`
- `data/generated/items/grade4_maths_launch_item_bank.json`
- `data/generated/lessons/grade4_maths_launch_lessons.json`
- `data/generated/assessment_blueprints/grade4_maths_launch_blueprints.json`
- `data/generated/study_plans/grade4_maths_launch_templates.json`

This is one of the stronger verified project areas.

## Security, Privacy, and Secrets

Positive controls:

- Production placeholder JWT secret guard exists.
- JWT keyring supports current/previous keys and `kid`.
- Token revocation by JTI and user-level revocation exists.
- Password hashing uses bcrypt with configurable rounds.
- PII encryption uses Fernet derived from `ENCRYPTION_KEY` and `ENCRYPTION_SALT`.
- Many route families enforce object-level learner authorization and active consent.
- Stripe webhook signature verification exists.
- Sensitive exception handlers avoid dumping DB/JWT internals by default.

Risks and incomplete areas:

- Practice session continuation routes are unauthenticated.
- `app/services/popia_service.py` contains TODOs for legal hold and export-offered checks.
- `app/api_v2_routers/auth_extended.py` has TODOs for export/deletion task enqueueing.
- `app/security/authorization.py` contains TODOs for repository-backed checks.
- `app/core/stripe_client.py` hardcodes Stripe checkout success/cancel URLs to `http://localhost:3000/dashboard...`.
- `docker-compose.prod.yml` injects production secrets directly as env vars rather than through a managed secret store.
- `bicep/container_apps.bicep` configures ACA ingress CORS with `allowedOrigins: ['*']`.

Secrets scan:

- Broad `detect-secrets scan --all-files` timed out.
- Narrowed detect-secrets scan over env examples, config, Docker, and selected config files completed.
- It reported unverified metadata hits in `.env.example` and `app/core/config.py`; these appear consistent with placeholder/default-secret surfaces, but I did not print or validate raw secret values.
- A direct regex scan that would print matching secret lines was not run because it was rejected as too risky for secret extraction during an audit.

## Deployment and Operations

Docker and Compose:

- `docker-compose.yml` runs API, docs, frontend, Prometheus, Alertmanager, Postgres, Redis, Grafana, Postgres exporter, and Redis exporter.
- `docker-compose.prod.yml` runs Nginx, API, frontend, Certbot, Postgres, and Redis.
- Production Compose lacks Prometheus/Grafana/exporters and lacks an ARQ worker.
- API image uses `docker/Dockerfile.v2` on Python 3.11, not the declared Python 3.12.3.
- Frontend image uses `docker/Dockerfile.frontend` and runs a production Next standalone server.
- Nginx production config rate-limits `/api/`, but the auth-specific limit targets `/api/v1/auth/`, while active auth routes are `/api/v2/auth/...`.

Azure/Bicep:

- `bicep/main.bicep` explicitly says it is a non-authoritative legacy draft.
- `bicep/container_apps.bicep` claims Azure Container Apps production deployment, but it appears API-only, not full-stack.
- ACA Bicep uses wildcard CORS and direct secret parameters.

Observability:

- App exposes custom Prometheus registry at `/metrics`.
- Readiness component metrics exist.
- Prometheus config scrapes API, inference, Postgres, and Redis exporters.
- Alerts and Alertmanager config exist.
- There is no evidence from this audit that these are running in a live environment.

Backups:

- Systemd backup service/timer files exist.
- ARQ database backup job exists.
- Production Compose does not deploy the ARQ worker that would run that job.
- Backup restore proof workflows/scripts exist, but I did not execute a live restore.

## Documentation Reality

The repository has extensive documentation and audit/evidence files, but the implementation does not fully match a release-ready story:

- Documentation says V2 and production-readiness work exists, and much of the scaffolding is real.
- Fresh checks show current frontend test/type health is broken.
- Fresh checks show full Ruff/code hygiene is not green.
- Existing coverage is below the declared threshold.
- Runtime versions disagree between `.python-version`, CI, Docker, and the remote venv.
- Some operational claims depend on workflows, cloud/staging secrets, or live infrastructure not available in this audit.

## Priority Findings

P0 - Fix frontend dependency/test health:

- Reconcile installed `node_modules` with `pnpm-lock.yaml`.
- Restore `dexie` resolution.
- Fix TypeScript implicit `any` errors.
- Fix Vitest TSX parsing under the current Vite/Vitest/Rolldown stack.
- Add a CI gate that actually runs from `app/frontend` with the same package manager version.

P0 - Fix practice session authorization:

- Require auth on `GET/POST /practice/sessions/{session_id}/*`.
- Persist session ownership or bind session id to learner/user.
- Re-check learner access and active consent on read/respond.
- Move session state out of process memory if these endpoints are production-facing.

P0 - Align Python runtime:

- Decide whether production is Python 3.12.3 or 3.11.
- Align `.python-version`, Dockerfiles, CI, compiled requirements, and remote venv.
- Avoid Python 3.11.0rc1 for production-like verification.

P0 - Restore basic syntax and correctness gates:

- Fix `scripts/maintenance/audit_todo_backlog.py:347`.
- Run `compileall` in CI over app/scripts.
- Expand Ruff CI beyond E9/F63/F7/F82 or explicitly separate release-blocking and non-blocking rules.
- Treat F821 as release-blocking everywhere.

P1 - Move schema repair out of app startup:

- Convert startup schema repairs into explicit Alembic migrations or a controlled migration job.
- Make `alembic current` and `alembic upgrade head` usable in documented local/CI environments.

P1 - Make background jobs durable:

- Deploy an ARQ worker or stop returning durable-looking job IDs for FastAPI BackgroundTasks.
- Fix ARQ settings attribute references.
- Wire worker deployment into Compose/ACA and health checks.

P1 - Harden production deployment config:

- Replace localhost Stripe redirects with environment-derived public URLs.
- Fix Nginx auth rate-limit path from `/api/v1/auth/` to `/api/v2/auth/`.
- Remove wildcard CORS from ACA Bicep.
- Decide whether Compose, ACA, or another target is authoritative and retire conflicting drafts.

P1 - Refresh coverage and quality evidence:

- Regenerate coverage from the current commit.
- Reconcile current 40.9 percent artifact with the declared 67 percent threshold.
- Make mypy and important security scans blocking if they are required for release claims.

P2 - Clean workspace hygiene:

- Keep `.venv`, `.next`, `node_modules`, coverage reports, and pyc files out of operational audit scans.
- Consider a cleanup target that is safe and explicit, then re-run counts/scans from a clean checkout.

## Verification Commands Run

- `git status --porcelain=v1 -b`
- `git rev-parse HEAD`
- file and directory inventories with `find`, `du`, and `git ls-files`
- FastAPI app route introspection under test settings
- `pytest --collect-only --no-cov -q`
- targeted backend smoke pytest subset
- `python -m compileall -q app scripts`
- `ruff check app tests scripts --output-format concise`
- `lint-imports --config .importlinter`
- `pnpm exec tsc --noEmit --pretty false`
- `pnpm exec vitest run --reporter=dot`
- `python scripts/validate_launch_content.py --strict`
- narrowed `detect-secrets scan`

## Audit Caveats

- I did not accept docs as proof; claims above are tied to code/config/checks.
- I did not run the full backend test suite, only collection and a smoke subset.
- I did not run live Docker Compose, live database migrations, live staging smoke, or live GitHub Actions.
- I did not modify source code.
- One ignored 0-byte SQLite temp file may remain under `temp/audit_smoke.sqlite` from test-environment setup; Git status remained clean.
