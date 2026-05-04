# EduBoost SA V2 — Agent TODO List
# Target: Raise overall project score from 7.4 → 10.0 / 10
# Generated: 2026-05-03 | Based on Technical Assessment Report v2
#
# EXECUTION RULES (from AGENT_INSTRUCTIONS.md):
#   - Follow TDD loop: write failing test → implement → green → commit
#   - Run `python scripts/popia_sweep.py --fail-on-issues` before every commit
#   - Update audits/roadmaps/V2_Outstanding_Task_Roadmap.md after every task
#   - Update audits/reports/Agentic_Execution_Report.md after every task
#   - A task is only DONE when: code ✅ | tests ✅ | docs ✅ | committed ✅
#
# TASK ORDER: Tasks are sequenced so each group builds on the previous.
#   Do NOT reorder within a group. Groups may be parallelised across agents.
# ─────────────────────────────────────────────────────────────────────────────

## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## GROUP A — CI/CD & REPOSITORY HYGIENE  (Score impact: CI/CD 8→10, DX 8→10)
## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1.  [x] Verify whether `.github/workflows/` already contains an active workflow
    file. If `ci.yml` at the repo root is the authoritative pipeline definition
    and is NOT mirrored there, copy it:
      `cp ci.yml .github/workflows/ci.yml`
    Delete the root-level `ci.yml` to avoid two sources of truth. Commit with
    message: `fix(ci): move pipeline to .github/workflows/ so GitHub Actions picks it up`.

2.  [x] Resolve the coverage threshold conflict: `ci.yml` enforces `--cov-fail-under=80`
    but `CONTRIBUTING.md` states 60% minimum. Align both to **80%** (the stricter,
    correct target). Update the coverage comment in `CONTRIBUTING.md` to read
    "80% minimum (CI enforces this)". Commit: `docs(contributing): align coverage
    threshold to CI gate of 80%`.

3.  [x] Add a `gitleaks` secrets-scanning job to `.github/workflows/ci.yml` that
    runs on every push and PR, scanning the full git history (`fetch-depth: 0`):
    ```yaml
    secrets-scan:
      name: Secrets Scan
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
          with:
            fetch-depth: 0
        - uses: gitleaks/gitleaks-action@v2
          env:
            GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    ```
    Add this job to the `needs` list of `production-promote`. Commit:
    `feat(ci): add gitleaks secrets scanning gate`.

4.  [x] Add a `pip-audit` dependency vulnerability scanning step to the `lint` job
    in `.github/workflows/ci.yml`:
    ```yaml
    - name: Audit Python dependencies
      run: |
        pip install pip-audit
        pip-audit -r requirements.txt -r requirements-ml.txt
    ```
    Commit: `feat(ci): add pip-audit Python dependency vulnerability scan`.

5.  [x] Add an `npm audit --audit-level=high` step to the `frontend` CI job to
    catch JavaScript dependency CVEs. Fail the job on high or critical severity.
    Commit: `feat(ci): add npm audit to frontend job`.

6.  [x] Add a Playwright E2E job to `.github/workflows/ci.yml` that runs after
    `integration-tests` passes, covering the full learner flow
    (diagnostic → study plan → lesson → parent portal):
    ```yaml
    e2e:
      name: E2E Tests (Playwright)
      needs: [integration-tests]
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with:
            node-version: "20"
        - run: npm ci
        - run: npx playwright install --with-deps chromium
        - run: npx playwright test
        - uses: actions/upload-artifact@v4
          if: failure()
          with:
            name: playwright-report
            path: playwright-report/
    ```
    Add `e2e` to the `needs` list of `production-promote`. Commit:
    `feat(ci): add Playwright E2E gate to CI pipeline`.

7.  [x] Add a separate V2-specific coverage report step to the `v2-smoke` CI job:
    ```yaml
    - name: V2 module coverage
      run: |
        pytest tests/unit/ \
          --cov=app.api_v2 \
          --cov=app.repositories \
          --cov=app.services \
          --cov=app.domain \
          --cov-report=term-missing \
          --cov-fail-under=80 \
          -v --tb=short
    ```
    Commit: `feat(ci): enforce 80% coverage threshold on V2 modules specifically`.

8.  [x] Enable GitHub's native **secret scanning** and **push protection** on the
    repository via Settings → Code Security → Secret scanning. Document the
    enablement in `SECURITY.md` under the Known Gaps table by changing
    "CI/CD secrets scanning not configured → Status: Complete". Commit:
    `docs(security): update known gaps — secrets scanning now active`.

9.  [x] Configure **Dependabot** for both Python and npm by creating
    `.github/dependabot.yml`:
    ```yaml
    version: 2
    updates:
      - package-ecosystem: "pip"
        directory: "/"
        schedule:
          interval: "weekly"
        open-pull-requests-limit: 5
      - package-ecosystem: "npm"
        directory: "/app/frontend"
        schedule:
          interval: "weekly"
        open-pull-requests-limit: 5
    ```
    Commit: `feat(deps): add Dependabot for automated dependency updates`.

10. [x] Remove the `scratch/` directory and the `mnt/user-data/outputs/` directory
    from version control, add both to `.gitignore`, and verify no sensitive
    content is present before deletion:
    ```bash
    git rm -r --cached scratch/ mnt/
    echo "scratch/" >> .gitignore
    echo "mnt/" >> .gitignore
    ```
    Commit: `chore: remove scratch dir and AI session artefact from tracked files`.

11. [x] Rename `gemini-code-1777601244294.md` to `docs/architecture/V2_ARCHITECTURE.md`
    to give it a stable, descriptive path:
    ```bash
    mkdir -p docs/architecture
    git mv gemini-code-1777601244294.md docs/architecture/V2_ARCHITECTURE.md
    ```
    Update all references in `AGENT_INSTRUCTIONS_V2.md`, `README.md`, and any
    file in `audits/` that links to the old filename. Commit:
    `docs: rename V2 architecture manifest to stable path`.

12. [x] Verify that `docker-compose.prod.yml` exists (it was listed in the CHANGELOG
    as added but returned 404 when fetched). If absent, create it with Nginx
    reverse-proxy, SSL termination via Let's Encrypt, and security headers
    (`X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`,
    `Content-Security-Policy`). Commit: `feat(docker): add production compose
    with Nginx SSL termination and security headers`.

13. [x] Publish GitHub Releases for `v0.1.0-beta` (2026-04-30) and `v0.2.0-rc1`
    (2026-05-01) to align the repository Releases page with the CHANGELOG. This
    also enables the `production-promote` CI job (which triggers on
    `github.event_name == 'release'`). Add release notes derived from the
    CHANGELOG entries for each version.


## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## GROUP B — SECURITY HARDENING  (Score impact: Security 7.0→10.0)
## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

14. [x] Implement JWT Refresh Token Rotation. In `app/core/security.py`:
    - Add `create_refresh_token(subject: str) -> str` using a 7-day expiry and
      a `"type": "refresh"` claim to distinguish from access tokens.
    - Reduce access token TTL from 24 hours to **15 minutes**.
    - In the auth router, set the refresh token as an HTTP-only, `SameSite=strict`,
      `Secure=true` cookie (never in the response body).
    - Add a `POST /api/v2/auth/refresh` endpoint that validates the refresh
      token cookie and returns a new access token + rotated refresh token cookie.
    - Add a `POST /api/v2/auth/logout` endpoint that clears the refresh token
      cookie and optionally adds the token to a Redis denylist (TTL = 7 days).
    Write integration tests in `tests/integration/test_auth_refresh.py` covering:
    happy-path refresh, expired refresh token rejection, logout cookie clearing,
    and reuse detection (if denylist is implemented). Commit:
    `feat(auth): implement JWT refresh token rotation with HTTP-only cookies`.

15. [x] Implement full Role-Based Access Control (RBAC). Define four roles in
    `app/domain/roles.py`: `Student`, `Parent`, `Teacher`, `Admin`. Add a `role`
    column to the `guardians` / `users` table via a new Alembic migration.
    Create FastAPI dependency `require_role(*roles)` in `app/core/security.py`
    that raises `HTTP 403` if the token's role claim is not in the allowed set.
    Apply `require_role` to every router endpoint according to the access matrix:
    - `Student`: read own lessons, diagnostic results, study plan
    - `Parent`: read learner data, manage consent, view parent portal
    - `Teacher`: read anonymised class-level analytics
    - `Admin`: all endpoints including erasure, RLHF export, user management
    Write tests in `tests/integration/test_rbac.py`. Commit:
    `feat(auth): implement 4-role RBAC with FastAPI dependency injection`.

16. [x] Add Bandit SAST (Static Application Security Testing) to the `lint` CI job:
    ```yaml
    - name: Run Bandit SAST
      run: |
        pip install bandit
        bandit -r app/ -ll -ii --exclude app/tests -f json -o bandit-report.json
    - uses: actions/upload-artifact@v4
      if: always()
      with:
        name: bandit-report
        path: bandit-report.json
    ```
    Fix any Bandit HIGH or CRITICAL findings before the job passes. Commit:
    `feat(ci): add Bandit SAST to lint job; fix all HIGH findings`.

17. [x] Add missing HTTP security headers to the FastAPI application in
    `app/api_v2.py` (or `app/api/main.py`) using a middleware:
    ```python
    from starlette.middleware.base import BaseHTTPMiddleware
    class SecurityHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; object-src 'none'"
            )
            return response
    ```
    Write a test confirming all headers are present on responses. Commit:
    `feat(security): add HTTP security headers middleware`.

18. [x] Wire **Azure Key Vault** into application startup for all production secrets.
    In `app/core/config.py`, when `APP_ENV == "production"`, source
    `JWT_SECRET`, `ENCRYPTION_KEY`, `ENCRYPTION_SALT`, `GROQ_API_KEY`, and
    `ANTHROPIC_API_KEY` from Key Vault using `azure-keyvault-secrets` +
    `azure-identity` (already in `requirements.txt`). Fall back to environment
    variables for `APP_ENV != "production"`. Document the required Key Vault
    secret names in `.env.example` and in `docs/architecture/V2_ARCHITECTURE.md`.
    Commit: `feat(config): source all production secrets from Azure Key Vault`.

19. [x] Implement a Redis token denylist for immediate JWT invalidation on logout
    and for admin-forced session revocation. Store invalidated JTI (JWT ID)
    claims in Redis with TTL equal to the token's remaining validity. Add a
    `jti` claim to all issued access tokens. Update the JWT validation
    middleware to reject tokens whose JTI is in the denylist. Write tests in
    `tests/unit/test_token_denylist.py`. Commit:
    `feat(auth): implement Redis JWT denylist for immediate token revocation`.

20. [x] Harden RabbitMQ (legacy) and Redis credentials. In `docker-compose.yml`
    (legacy path), replace the default `guest/guest` RabbitMQ credentials with
    environment-variable-driven values (`RABBITMQ_USER`, `RABBITMQ_PASSWORD`).
    Update `.env.example` to document these as REQUIRED in production. Confirm
    the V2 path has no RabbitMQ dependency. Commit: `fix(docker): remove
    default RabbitMQ guest/guest credentials from compose files`.


## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## GROUP C — POPIA COMPLIANCE COMPLETION  (Score impact: POPIA 9.0→10.0)
## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

21. [x] Complete end-to-end verification of **Right to Erasure (POPIA §24)**. Write
    a comprehensive integration test in `tests/popia/test_right_to_erasure.py`:
    1. Create guardian + learner + active consent + lesson record + diagnostic session
    2. Call `DELETE /api/v2/learners/{id}` with a valid Guardian JWT
    3. Assert consent record is revoked (`is_active = False`)
    4. Assert learner PII fields are nulled/soft-deleted (`display_name`, `dob`, `school`)
    5. Assert guardian email is not retrievable in plaintext
    6. Assert a purge BackgroundTask has been queued (mock the task and assert it was called)
    7. Assert the LLM service raises `ConsentRequiredError` when called with the now-deleted learner's ID
    8. Assert an audit log entry exists for the erasure event
    Run `pytest tests/popia/test_right_to_erasure.py -v` and confirm green.
    Update `SECURITY.md` Known Gaps table: "Right-to-erasure → Status: Complete".
    Note: implementation scaffold moved from `temp/code_1/` into
    `tests/popia/test_right_to_erasure.py` for live integration.
    Commit: `test(popia): complete end-to-end right-to-erasure verification`.

22. [x] Complete the **Consent Audit Trail** across all workflows where consent state
    changes. Audit every code path that calls `grant()`, `revoke()`, and
    `execute_erasure()` on `ConsentService`. Ensure each path produces an audit
    log entry via `fourth_estate.py` (legacy) or the V2 append-only audit table.
    Write tests in `tests/popia/test_consent_audit_trail.py` asserting that an
    audit record is created for: consent grant, consent revocation, annual
    renewal, erasure request, and failed consent check (rejected access attempt).
    Update `SECURITY.md` Known Gaps: "Consent audit trail → Status: Complete".
    Note: implementation scaffold moved from `temp/code_1/` into
    `tests/popia/test_consent_audit_trail.py` for live integration.
    Commit: `feat(popia): complete consent audit trail across all workflows`.

23. [x] Implement the **V2 Audit Service** backed by an append-only PostgreSQL table,
    replacing the Redis stream dependency for the V2 path. Create an Alembic
    migration (`0005_v2_audit_events.py`):
    ```sql
    CREATE TABLE audit_events (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        event_type  TEXT NOT NULL,
        actor_id    UUID,
        resource_id UUID,
        payload     JSONB NOT NULL DEFAULT '{}',
        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE RULE no_update_audit AS ON UPDATE TO audit_events DO INSTEAD NOTHING;
    CREATE RULE no_delete_audit AS ON DELETE TO audit_events DO INSTEAD NOTHING;
    CREATE INDEX idx_audit_events_actor ON audit_events(actor_id);
    CREATE INDEX idx_audit_events_type  ON audit_events(event_type);
    CREATE INDEX idx_audit_events_ts    ON audit_events(created_at DESC);
    ```
    Create `app/repositories/audit_repository.py` with an async `append()`
    method. Inject `AuditRepository` into all V2 services that currently call
    `fourth_estate.py`. Write tests in `tests/unit/test_audit_repository.py`
    confirming that UPDATE and DELETE on audit records are rejected at the
    database level. Commit: `feat(v2): implement PostgreSQL append-only V2 audit service`.
    Note: implementation scaffold moved from `temp/code_1/` into
    `alembic/versions/0006_v2_audit_events.py`,
    `app/repositories/audit_repository.py`, and
    `tests/unit/test_audit_repository.py` for live integration.

24. [x] Implement a scheduled **POPIA Annual Consent Renewal Reminder**. Add a
    FastAPI `BackgroundTasks`-compatible scheduler (or Celery Beat in the legacy
    path) that runs daily and queries for `ParentalConsent` records where
    `expires_at` is within 30 days. For each expiring record, dispatch a
    SendGrid email via the existing `sendgrid` dependency with a renewal link.
    Write a test in `tests/integration/test_consent_renewal.py`. Commit:
    Note: implementation scaffold moved from `temp/code_1/` into
    `app/api_v2_routers/consent_renewal.py`, `app/jobs/consent_renewal_job.py`,
    `app/services/consent_renewal_service.py`, and
    `tests/integration/test_consent_renewal.py` for live integration.
    `feat(popia): add annual consent renewal reminder email`.

25. [x] Implement **PII Minimisation Audit** on the RLHF export pipeline. In
    `RLHFService`, before any preference dataset is exported (OpenAI or
    Anthropic format), run a final regex scan across all free-text fields using
    `bleach` and `phonenumbers` to detect any residual PII (names, phone
    numbers, email addresses, SA ID numbers). Raise `PIISweepError` and abort
    the export if any PII is detected. Write tests in
    Note: implementation scaffold moved from `temp/code_1/` into
    `app/services/pii_sweep.py` and `tests/popia/test_rlhf_pii_scrubbing.py`
    for live integration.
    `tests/popia/test_rlhf_pii_scrubbing.py`. Commit:
    `feat(popia): add pre-export PII minimisation gate to RLHF pipeline`.


## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## GROUP D — V2 MIGRATION COMPLETION  (Score impact: Architecture 7.5→10.0)
## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

26. [x] Add the Redis healthcheck to `docker-compose.v2.yml` and update the `api`
    service `depends_on` block to wait for Redis healthy before starting:
    ```yaml
    redis:
      healthcheck:
        test: ["CMD", "redis-cli", "ping"]
        interval: 10s
        timeout: 5s
        retries: 5
    # api.depends_on:
      redis:
        condition: service_healthy
    ```
    Commit: `fix(docker): add Redis healthcheck to V2 compose to prevent race condition`.

27. Complete V2 router parity for all legacy endpoints. For each router in
    `app/api/routers/` (auth, learners, consent, diagnostic, lessons,
    study-plans, parent-portal), verify a corresponding V2 router exists in
    `app/api_v2_routers/`. Implement any missing V2 routers, ensuring each:
    - calls a service from `app/services/` (not direct DB access)
    - uses `app/repositories/` for all DB operations
    - calls `ConsentService.require_active_consent()` before any learner data access
    - uses the `require_role()` dependency from task 15
    Once a V2 router reaches full parity, move the corresponding legacy router to
    `app/legacy/` and add a deprecation comment. Commit per router:
    `feat(v2): complete V2 [router-name] router; move legacy to app/legacy/`.
    Progress note (2026-05-04): the stale V2 parent router was replaced with a
    working parent-dashboard/erasure router that imports cleanly against the
    current `app/core`, `app/models`, and `app/services` layout. Full parity
    across every legacy endpoint family is still pending.

28. [x] Enforce strict domain layer import boundaries. In each `app/api/`,
    `app/services/`, and `app/repositories/` `__init__.py`, add import-time
    assertions or use `import-linter` to prevent boundary violations (e.g.,
    `app/api/` must not import from `app/repositories/` directly). Add
    `import-linter` to `requirements-dev.txt` and create `.importlinter` config:
    ```ini
    [importlinter]
    root_package = app
    [[contracts]]
    name = API must not import repositories
    type = forbidden
    source_modules = app.api
    forbidden_modules = app.repositories
    ```
    Add `lint-imports` to the `lint` CI job. Commit:
    `feat(arch): enforce DDD import boundaries with import-linter`.
    Note: the useful `temp/code_4/` scaffold was merged into
    `.importlinter`, `requirements-dev.txt`, and `.github/workflows/ci-cd.yml`,
    then validated with a passing `lint-imports` run.

29. [x] Migrate `app/api/core/` configuration to `app/core/` (the V2 canonical
    location). Consolidate `config.py`, `security.py`, and `logging.py` into
    the V2 `app/core/` module. Update all imports throughout the codebase.
    Ensure structured JSON logging is active from application startup with
    `APP_ENV`, `APP_VERSION`, and `REQUEST_ID` fields on every log line.
    Commit: `refactor(v2): consolidate core config/security/logging into app/core/`.
    Note: the `temp/code_4/` metrics/logging/app wiring was folded into
    `app/core/logging.py`, `app/core/middleware.py`, `app/core/metrics.py`,
    and the V2 app startup path, then verified by `tests/integration/test_security_headers.py`,
    `tests/unit/test_imports.py`, and the V2 smoke suite.

30. Implement the V2 `BackgroundTasks`-based async pattern across all service
    operations that were previously handled by Celery tasks. This includes:
    - Lesson generation (decouple HTTP response from LLM call)
    - Study plan generation
    - POPIA §24 data purge
    - RLHF export processing
    - Consent renewal reminder dispatch (from task 24)
    Each task should return a `202 Accepted` with a job ID, and a
    `GET /api/v2/jobs/{job_id}` endpoint backed by Redis that returns the task
    status and result when complete. Write integration tests for each. Commit:
    `feat(v2): replace Celery async tasks with FastAPI BackgroundTasks + Redis job store`.

31. Update `anthropic` SDK from `0.40.0` to the latest stable version. Verify
    Claude Sonnet 4 model strings are used correctly throughout
    `app/services/lesson_service.py` (or equivalent). Run the full test suite
    after the upgrade. Commit: `chore(deps): upgrade anthropic SDK to latest stable`.

32. Remove `mkdocs`, `mkdocs-material`, and `mkdocstrings` from `requirements.txt`
    and add them to a new `requirements-docs.txt`. Update `docker/Dockerfile.v2`
    to install only `requirements.txt` in the production stage and
    `requirements-docs.txt` in the `docs` service build stage. Confirm the
    `mkdocs serve` command in `docker-compose.v2.yml` still works. Commit:
    `chore(deps): move docs dependencies to requirements-docs.txt`.

33. Fully decommission the legacy path once all V2 routers are complete (after
    task 27). Archive the legacy directory:
    - Move `app/api/` (legacy) → `app/legacy/` with a `DEPRECATED.md`
    - Remove `docker-compose.yml` (legacy) from the root; rename
      `docker-compose.v2.yml` → `docker-compose.yml`
    - Update `README.md` to remove all references to the legacy runtime
    - Update `CONTRIBUTING.md` "Running the Stack" section
    Commit: `feat(v2): decommission legacy runtime; V2 is now the sole runtime`.


## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## GROUP E — PEDAGOGICAL VALIDITY  (Score impact: Pedagogical 6.0→10.0)
## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

34. Create the IRT Item Bank Alembic seed migration (`0006_irt_item_bank.py`)
    with a minimum of **500 calibrated 2PL IRT items** across Grades R–7 and
    all CAPS subjects (Mathematics, English Home Language/First Additional
    Language, Life Skills, Natural Sciences & Technology, Social Sciences,
    Creative Arts, Economic & Management Sciences). Each item must have:
    - `grade` (R, 1–7)
    - `subject` (CAPS-aligned)
    - `topic` (CAPS strand)
    - `language` (en, zu, af, xh)
    - `a` (discrimination parameter: typically 0.5–2.5)
    - `b` (difficulty parameter: typically -3 to +3, logit scale)
    - `question_text`, `options` (JSON array), `correct_option_index`
    Validate parameters against the 2PL model equation:
      `P(correct|θ) = 1 / (1 + exp(-a(θ - b)))`
    ensuring items produce monotonically increasing ICC curves. Engage a
    certified CAPS educator to review and sign off on the content. Commit:
    `feat(irt): add 500+ calibrated 2PL IRT item bank via Alembic seed migration`.

35. Implement the **Ether Cold-Start Micro-Diagnostic** (V2 Manifest Task 3.2).
    Create a `POST /api/v2/onboarding/archetype` endpoint that accepts 5
    answers to onboarding questions and returns an initial archetype
    classification (Keter, Chokhmah, Binah, Chesed, Gevurah, Tiferet,
    Netzach, Hod, Yesod, or Malkuth) computed via a Bayesian prior update on
    archetype probability vectors. Store the result in the learner's session
    profile. The 5 questions should probe: learning pace preference, visual vs
    text preference, motivation driver, peer vs solo preference, and response to
    challenge. Write tests in `tests/unit/test_ether_cold_start.py` confirming
    that all 10 archetypes are reachable from plausible answer combinations.
    Commit: `feat(ether): implement cold-start micro-diagnostic for session-1 archetype classification`.

36. Implement the **Gap-Probe Cascade** using the IRT item bank from task 34.
    The cascade should:
    1. Initialise θ (learner ability) at 0.0 (grade-level average)
    2. Select the next item using Maximum Fisher Information at the current θ estimate
    3. Update θ using the Expected A Posteriori (EAP) estimator after each response
    4. Halt when the standard error of θ falls below 0.3 or after 20 items
    5. Map the final θ estimate to a CAPS grade-level equivalence
    6. Generate a ranked list of knowledge gap topics for the study plan
    Write tests in `tests/unit/test_irt_gap_probe.py` validating EAP convergence
    on synthetic response vectors. Commit:
    `feat(irt): implement adaptive Gap-Probe Cascade with EAP estimation and MFI item selection`.

37. Implement CAPS curriculum alignment validation. Create a
    `CAPSAlignmentValidator` in `app/services/caps_validator.py` that, given a
    generated lesson's topic and grade, asserts the content falls within the
    CAPS curriculum scope for that term. Surface a `caps_aligned: bool` field
    in the `LessonResponse` schema. If `caps_aligned` is `False`, the Executive
    service must retry generation with a corrected prompt. Write tests in
    `tests/unit/test_caps_alignment.py`. Commit:
    `feat(pedagogy): add CAPS curriculum alignment validation to lesson generation`.


## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## GROUP F — AI LAYER & COST CONTROL  (Score impact: Scalability 7.0→10.0)
## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

38. Implement **Fully Asynchronous LLM Inference** (V2 Manifest Phase 2, Task 2.1).
    Replace any synchronous `anthropic.Anthropic()` client calls with
    `anthropic.AsyncAnthropic()` and `await` all `.messages.create()` calls.
    Replace any synchronous Groq client calls with the async Groq client.
    Confirm via load test (`locust` or `pytest-benchmark`) that the FastAPI
    worker pool is not blocked during LLM network calls. Commit:
    `feat(llm): migrate all LLM clients to fully async — eliminate event-loop starvation`.

39. Implement **Strict Schema Enforcement** in the Judiciary (V2 Manifest Phase 2,
    Task 2.2). Replace all string-parsing of LLM outputs with:
    - Groq: `response_format={"type": "json_object"}` + `TypeAdapter` validation
    - Anthropic Claude: Tool Use / structured output mapped directly to Pydantic models
    Define Pydantic models for `LessonContent`, `StudyPlanContent`, and
    `DiagnosticFeedback` in `app/domain/`. The Judiciary `stamp()` method must
    validate the LLM output against these models and raise `JudiciaryRejection`
    on failure (triggering a retry). Write tests that inject malformed LLM
    responses and assert `JSONDecodeError` is mathematically impossible at
    runtime. Commit: `feat(judiciary): enforce strict Pydantic schema on all LLM outputs`.

40. Implement the **Redis-backed Semantic Caching Layer** (V2 Manifest Phase 2,
    Task 2.3). In `app/services/lesson_service.py`:
    - Compute a cache key from `(grade, topic_slug, language_code, archetype)`.
    - Check Redis before calling the LLM; return the cached `LessonResponse` if
      present (target: <50ms p95).
    - Set the Redis key with `TTL = 3600` seconds on cache write.
    - Add a `cache_hit: bool` field to `LessonResponse` for telemetry.
    Write tests confirming identical requests serve from cache and that a
    cache miss triggers the LLM call. Commit:
    `feat(llm): add Redis semantic caching — identical requests served in <50ms`.

41. Implement **Daily Token/Request Quotas per User** (V2 Manifest Phase 2,
    Task 2.3). In `app/core/rate_limiter.py`:
    - Free tier: 20 AI requests/day
    - Premium tier: unlimited (Stripe webhook updates the tier in Redis; see task 51)
    - Use Redis `INCR` + `EXPIRE` for the daily counter keyed on `user_id:YYYYMMDD`
    - Return `HTTP 429 Too Many Requests` with `Retry-After: seconds_until_midnight`
      when the quota is exceeded
    Apply the quota check as a FastAPI dependency on all lesson-generation and
    diagnostic endpoints. Write tests in `tests/integration/test_rate_limits.py`.
    Commit: `feat(ai): implement daily AI request quotas per user tier`.

42. Add **LLM Token Cost Telemetry** to the Prometheus metrics layer. In
    `app/api/core/metrics.py` (or `app/core/metrics.py`):
    ```python
    LLM_TOKENS_TOTAL = Counter(
        "eduboost_llm_tokens_total",
        "Total LLM tokens consumed",
        ["provider", "model", "operation"]
    )
    LLM_COST_USD = Gauge(
        "eduboost_llm_estimated_cost_usd_daily",
        "Estimated daily LLM cost in USD",
        ["provider"]
    )
    ```
    Instrument every LLM call to record input + output token counts. Add a
    Grafana panel for "Daily Token Consumption by Provider" and "Projected
    Monthly Cost". Commit: `feat(observability): add LLM token cost telemetry to Prometheus`.


## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## GROUP G — OBSERVABILITY COMPLETION  (Score impact: Observability 7.5→10.0)
## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

43. Create `prometheus/alerts.yml` with Alertmanager rules for all SLOs:
    ```yaml
    groups:
      - name: eduboost_critical
        rules:
          - alert: LLMProviderDown
            expr: rate(eduboost_llm_requests_total{status="error"}[5m]) > 0.5
            for: 2m
            labels: { severity: critical }
          - alert: ConsentGateFailureSpike
            expr: rate(eduboost_consent_failures_total[5m]) > 0.05
            for: 2m
            labels: { severity: critical }
          - alert: LessonGenerationHighLatency
            expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{handler=~".*/lessons.*"}[5m])) > 15
            for: 5m
            labels: { severity: warning }
          - alert: JudiciaryHighRejectionRate
            expr: rate(eduboost_judiciary_rejections_total[5m]) / rate(eduboost_judiciary_stamps_total[5m]) > 0.1
            for: 5m
            labels: { severity: warning }
          - alert: DiagnosticDropOffSpike
            expr: rate(eduboost_diagnostic_abandonments_total[10m]) > 0.3
            for: 10m
            labels: { severity: warning }
    ```
    Wire `alerts.yml` into `prometheus.yml` via `rule_files`. Add an
    Alertmanager container to `docker-compose.v2.yml` configured to route
    alerts to a Slack webhook (environment variable `ALERTMANAGER_SLACK_WEBHOOK`).
    Commit: `feat(observability): add Prometheus alerting rules and Alertmanager Slack routing`.

44. Implement **PostHog Product Telemetry** at the API gateway level
    (V2 Manifest Phase 5, Task 5.1). Instrument the following events without
    exposing PII (use `pseudonym_id` as the PostHog distinct ID):
    - `diagnostic_started`, `diagnostic_completed`, `diagnostic_abandoned`
    - `lesson_viewed`, `lesson_completed`, `lesson_feedback_submitted`
    - `study_plan_generated`
    - `consent_granted`, `consent_revoked`
    - `parent_portal_viewed`
    Use PostHog's Python SDK in a middleware or as a FastAPI background task
    so telemetry is non-blocking. Add `posthog` to `requirements.txt`. Write
    a test confirming `pseudonym_id` is used and no PII fields are present
    in the event properties. Commit:
    `feat(analytics): add PostHog product telemetry with pseudonym_id isolation`.

45. Add an **uptime/synthetic monitoring** endpoint for the production ACA
    deployment. Create `GET /api/v2/health/deep` that checks:
    - PostgreSQL connectivity (simple `SELECT 1`)
    - Redis connectivity (`PING`)
    - LLM provider reachability (lightweight test call or timeout probe)
    - Judiciary service health
    Return `200 OK` with a JSON body showing each component's status, or
    `503 Service Unavailable` if any critical component is down. Configure an
    Azure Monitor availability test (or UptimeRobot) against
    `https://your-domain/api/v2/health/deep` with a 1-minute check interval.
    Commit: `feat(observability): add deep health endpoint and configure uptime monitoring`.


## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## GROUP H — FRONTEND & UX COMPLETION  (Score impact: DX 8→10, Test 6.5→10.0)
## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

46. Complete the **TypeScript migration** of the Next.js frontend. Convert all
    remaining `.js` and `.jsx` files in `app/frontend/src/` to `.ts` / `.tsx`.
    Focus first on `src/lib/api/` (the typed API service layer) to enforce
    contract correctness between frontend and backend schemas. Enable
    `"strict": true` in `tsconfig.json`. Fix all resulting type errors. Run
    `npm run type-check` to confirm zero errors. Commit:
    `refactor(frontend): complete TypeScript migration — strict mode enabled`.

47. Configure **Jest coverage** for the frontend with a minimum threshold of
    **80%** (matching the backend CI gate) for all components under
    `src/components/eduboost/` and all API service layer files under
    `src/lib/api/`. Add to `package.json`:
    ```json
    "jest": {
      "coverageThreshold": {
        "global": { "branches": 80, "functions": 80, "lines": 80 }
      }
    }
    ```
    Write missing tests until the threshold is met. Add a coverage upload step
    to the `frontend` CI job. Commit:
    `test(frontend): add Jest coverage threshold (80%) for components and API layer`.

48. Implement the **Parent Trust Dashboard** frontend + backend
    (V2 Manifest Phase 5, Task 5.2). Backend: expose
    `GET /api/v2/parents/{guardian_id}/dashboard` returning:
    - Aggregated gap-probe results per learner (top 3 knowledge gaps)
    - AI-generated 3-sentence progress summary (LLM-generated, pseudonymised)
    - Lesson completion rate (7-day rolling)
    - Streak data
    - Right-to-access export link (`GET /api/v2/parents/{id}/export`)
    Frontend: implement the `src/app/parent-portal/` page with Chart.js or
    Recharts visualisations for the above data. Write Playwright E2E tests for
    the parent portal flow. Commit:
    `feat(parent-portal): implement Parent Trust Dashboard with AI progress summary`.

49. Implement the **PWA offline sync** capability. Ensure the service worker
    (`manifest.json` + service worker script) correctly caches the last-loaded
    lesson and diagnostic session for offline access. Test with Chrome DevTools
    Network → Offline mode. The learner should be able to complete a cached
    lesson while offline and sync their response when connectivity is restored
    (using a `POST /api/v2/lessons/sync` endpoint that accepts queued responses).
    Write a Playwright test simulating offline completion + sync. Commit:
    `feat(pwa): implement offline lesson caching and response sync`.


## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## GROUP I — DEPENDENCY & INFRASTRUCTURE  (Score impact: Deps 6.5→10.0, Arch→10)
## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

50. Split `requirements.txt` into environment-specific files:
    - `requirements/base.txt` — runtime only (no test, no docs, no ML)
    - `requirements/dev.txt` — `-r base.txt` + pytest, ruff, mypy, bandit, faker, factory-boy
    - `requirements/docs.txt` — mkdocs, mkdocs-material, mkdocstrings (moved from task 32)
    - `requirements/ml.txt` — already separate; standardise location under `requirements/`
    Update all Dockerfiles to install only `requirements/base.txt` in the
    production stage. Update CI jobs to install `requirements/dev.txt`.
    Update `CONTRIBUTING.md` setup instructions. Commit:
    `chore(deps): split requirements into base/dev/docs/ml environment files`.

51. Implement the **Stripe Subscription Engine** (V2 Manifest Phase 5, Task 5.3).
    Add `stripe` to `requirements/base.txt`. Implement:
    - `POST /api/v2/billing/create-checkout-session` — creates a Stripe Checkout
      session for the Premium tier
    - `POST /api/v2/billing/webhook` — handles `customer.subscription.created`,
      `customer.subscription.deleted`, and `invoice.payment_failed` events
    - On subscription created: set `user.tier = "premium"` in Redis and Postgres
    - On subscription deleted / payment failed: revert to `"free"` tier
    Tie the Premium tier to unlimited daily AI quota (task 41). Write tests in
    `tests/integration/test_stripe_webhooks.py` using Stripe's webhook fixture
    library. Commit: `feat(billing): implement Stripe subscription engine with quota gating`.

52. Add Docker layer caching to the `image-scan` CI job to reduce cold build
    times:
    ```yaml
    - uses: docker/setup-buildx-action@v3
    - uses: docker/build-push-action@v5
      with:
        context: .
        file: docker/Dockerfile.api
        tags: eduboost-api:scan
        cache-from: type=gha
        cache-to: type=gha,mode=max
        load: true
    ```
    Commit: `perf(ci): add GHA layer caching to Docker image build in CI`.

53. Implement **Azure Key Vault secret rotation** support. In `app/core/config.py`,
    add a background task that re-fetches Key Vault secrets every 6 hours and
    hot-reloads them without requiring an application restart. This prevents
    stale credentials after a rotation event. Write a test mocking the Key Vault
    client to confirm the reload cycle fires correctly. Commit:
    `feat(config): add 6-hour Key Vault secret rotation hot-reload`.

54. Pin all `requirements/base.txt` dependencies using `pip-compile`
    (`pip-tools`). Create `requirements/base.in` as the human-editable source
    of truth, and generate `requirements/base.txt` from it via:
      `pip-compile requirements/base.in -o requirements/base.txt`
    Add `pip-compile` to `requirements/dev.txt` and document the update process
    in `CONTRIBUTING.md`. Commit:
    `chore(deps): adopt pip-compile for reproducible dependency locking`.


## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## GROUP J — DOCUMENTATION & GA RELEASE  (Score impact: all domains → 10.0)
## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

55. Update `SECURITY.md` Known Gaps table to reflect all completed tasks from
    Groups B and C. All six self-disclosed gaps must read "Status: Complete"
    with a link to the commit that closed them. Add new entries for any
    additional security controls added (Key Vault, RBAC, denylist, headers).
    Commit: `docs(security): close all known gaps in SECURITY.md`.

56. Update `audits/roadmaps/V2_Outstanding_Task_Roadmap.md` to mark all
    completed tasks from this TODO list as done, using the agent completion
    standard (code ✅ | tests ✅ | docs ✅ | committed ✅). Commit:
    `docs(audit): update V2 roadmap — all TODO tasks completed`.

57. Update `audits/reports/Agentic_Execution_Report.md` with a full summary of
    all 57 tasks executed, grouped by category, with commit hashes, test
    results, and any architectural decisions made during implementation. Commit:
    `docs(audit): final agent execution report for TODO list completion`.

58. Update `mkdocs.yml` and the MkDocs documentation pages to cover all new V2
    modules: `api_v2`, `api_v2_routers/*`, `repositories/*`, `services/*`,
    `domain/*`, `core/*`, the audit service, the IRT engine, and the Ether
    archetype engine. Ensure `mkdocstrings` generates API references from
    docstrings for all public methods. Verify `mkdocs build --strict` passes
    with zero warnings. Commit: `docs: complete MkDocs documentation for all V2 modules`.

59. Update `README.md` to reflect the final V2 state:
    - Remove all references to the legacy runtime and Celery/RabbitMQ
    - Update the Quick Start to use the single `docker compose up --build`
    - Update the "Current State" section to remove all ⚠️ Beta caveats
    - Add a "Architecture" section linking to `docs/architecture/V2_ARCHITECTURE.md`
    - Add badges for: CI/CD status, coverage %, security scan, POPIA compliance,
      CAPS alignment
    Commit: `docs(readme): update README to reflect V2 GA state`.

60. Tag and publish **v1.0.0** as a GitHub Release. Before tagging:
    - Confirm all 59 preceding tasks are committed and CI is green on master
    - Run the full `pytest` suite, Playwright E2E suite, and POPIA sweep
    - Run `python scripts/popia_sweep.py --fail-on-issues` — must produce 0 issues
    - Verify `alembic check` reports no pending migrations
    - Confirm the production promotion gate (task 1's `production-promote` job)
      triggers correctly and completes the Kubernetes rollout
    - Publish the GitHub Release with release notes summarising all changes
      since v0.2.0-rc1
    Commit: `chore(release): tag v1.0.0 — GA release`.

# ─────────────────────────────────────────────────────────────────────────────
# EXPECTED SCORE AFTER COMPLETION
# ─────────────────────────────────────────────────────────────────────────────
#
#  Domain                  | Before | After | Tasks Responsible
#  ─────────────────────────|────────|───────|──────────────────────────────
#  Architecture Design      |  7.5   | 10.0  | 27, 28, 29, 30, 33
#  POPIA / Compliance       |  9.0   | 10.0  | 21, 22, 23, 24, 25
#  CI/CD Pipeline           |  8.0   | 10.0  | 1–9, 52
#  Security Posture         |  7.0   | 10.0  | 14–20, 55
#  Test Strategy            |  6.5   | 10.0  | 6, 7, 21, 22, 46, 47
#  Observability            |  7.5   | 10.0  | 42, 43, 44, 45
#  Dependency Management    |  6.5   | 10.0  | 31, 32, 50, 54, 9
#  Developer Experience     |  8.0   | 10.0  | 10, 11, 12, 13, 56, 57, 59
#  Pedagogical Validity     |  6.0   | 10.0  | 34, 35, 36, 37
#  Scalability Readiness    |  7.0   | 10.0  | 38, 39, 40, 41, 49, 51, 53
#  Domain & Cultural Depth  |  9.0   | 10.0  | 35, 37, 48
#  ─────────────────────────|────────|───────|──────────────────────────────
#  OVERALL                  |  7.4   | 10.0  | All 60 tasks
# ─────────────────────────────────────────────────────────────────────────────
