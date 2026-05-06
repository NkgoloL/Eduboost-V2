# EduBoost V2 — Implementation Report

**Purpose:** Rolling V2-specific implementation log, mirroring the existing audit report structure used elsewhere in the repository.

---

### [2026-05-01] V2 Baseline Scaffold
**Status:** Complete  
**What changed:**
- Added V2 modular-monolith package boundaries under `app/core`, `app/domain`, `app/repositories`, and `app/services`
- Added V2 configuration, security, logging, domain entities, and repository abstractions
- Added `app/api_v2.py`

**Why:**
- Establish the initial V2 architectural boundary without destabilizing the current runtime.

---

### [2026-05-01] V2 Vertical Slice Expansion
**Status:** Complete  
**What changed:**
- Added V2 learner, audit, auth, study-plan, parent-report, diagnostic, and quota services
- Added V2 runtime path with `docker-compose.v2.yml`
- Added MkDocs + mkdocstrings automated documentation baseline

**Why:**
- Move the project from abstract V2 intent toward an actual parallel V2 product surface.

---

### [2026-05-01] V2 Tracking Structure Replication
**Status:** Complete  
**What changed:**
- Added dedicated V2 roadmap, implementation report, review, and docs pages
- Added V2-specific agent instructions file

**Why:**
- Mirror the current project’s multi-file tracking and governance style so V2 progress is visible and auditable independently.

---

### [2026-05-01] V2 Route Surface Promotion & Runtime Guidance
**Status:** Complete  
**What changed:**
- Added dedicated `app/api_v2_routers/*` modules for auth, learners, diagnostics, study plans, parents, and audit
- Refactored `app/api_v2.py` to consume dedicated V2 routers instead of inline endpoints
- Updated README, contributing guide, docs, and CI to promote the V2 path as the preferred runtime and mark the legacy path as compatibility mode

**Why:**
- Push the repository toward a true parallel V2 application rather than a single-file alternative entrypoint.

---

### [2026-05-01] V2 Route Family Expansion
**Status:** Complete  
**What changed:**
- Added V2 services and routers for lessons, gamification, system, and assessments
- Updated the V2 API entrypoint to include all remaining major route families
- Expanded automated docs coverage for the added V2 service modules

**Why:**
- Reduce the remaining gap between the legacy route surface and the V2 route surface.

---

### [2026-05-02] V2 Stabilisation Pass
**Status:** Partially verified  
**What changed:**
- Repaired `app/core/config.py` so the V2 settings module is syntactically valid and includes current runtime knobs
- Added the missing `app/services/` package and compatibility service modules expected by V2 routers/tests
- Added `app/domain/models.py`, `app/domain/entities.py`, and `app/domain/api_v2_models.py` compatibility modules
- Updated Alembic to import V2 ORM metadata from `app.models`
- Added `app/api/version.py`, RBAC compatibility helpers, and V2 health metadata
- Aligned the frontend API default with `/api/v2`
- Added a frontend service to `docker-compose.v2.yml`
- Updated CI to run on `master`, use the repository dev requirements, run frontend lint/type checks, and include the POPIA prompt sweep

**Verification notes:**
- Full dependency installation is blocked on this Windows/Python 3.13 environment because the project targets Python 3.11 and `scikit-learn==1.5.0` attempts a local compile.
- A partial dependency install was attempted to support import smoke tests, but pip later hit a memory error in this environment.

**Why:**
- The V2 tree had import/runtime blockers before deeper TODO work could be safely validated.

---

### [2026-05-03] V2 Security Hardening Batch (Tasks 18-20)
**Status:** Complete  
**What changed:**
- Wired `app/core/config.py` to load `JWT_SECRET`, `ENCRYPTION_KEY`, `ENCRYPTION_SALT`, `GROQ_API_KEY`, and `ANTHROPIC_API_KEY` from Azure Key Vault in production
- Documented the required Key Vault secret names in `.env.example` and `docs/architecture/ARCHITECTURE.md`
- Added unit coverage for production/non-production Key Vault behavior in `tests/unit/test_config_key_vault.py`
- Completed Redis-backed JWT denylist verification in `tests/unit/test_token_denylist.py`
- Updated the auth refresh/logout/revoke-all flow to persist rotated refresh tokens and revoke cookie-backed refresh tokens on logout
- Removed legacy `guest/guest` RabbitMQ guidance from top-level docs and replaced legacy integration examples with environment-driven credentials
- Fixed the missing `BaseHTTPMiddleware` import in `app/api_v2.py` so the V2 smoke suite can import and execute the app

**Verification:**
- `.venv/bin/python -m py_compile app/api_v2.py app/core/config.py app/core/security.py app/core/token_revocation.py app/api_v2_routers/auth.py tests/unit/test_config_key_vault.py tests/unit/test_token_denylist.py`
- `.venv/bin/python -m pytest tests/unit/test_config_key_vault.py tests/unit/test_token_denylist.py -v --tb=short -o addopts=""`
- `.venv/bin/python -m pytest tests/smoke -v --tb=short -o addopts=""`

**Why:**
- Close the remaining production-secret, token-revocation, and legacy-broker hardening gaps without reintroducing RabbitMQ into the V2 runtime.
