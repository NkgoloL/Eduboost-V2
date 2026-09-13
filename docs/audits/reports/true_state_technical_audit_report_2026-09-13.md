---
title: "EduBoost V2 Comprehensive True State Technical Audit Report"
status: active
owner: engineering
reviewers: [engineering, architecture, security]
audience: internal
source_of_truth: false
last_reviewed: 2026-09-13
review_interval_days: 90
---

# Comprehensive Technical Audit Report: The True State of EduBoost V2

**Document ID:** `AUDIT-REP-2026-09-13-COMPREHENSIVE-TRUE-STATE`  
**Date of Audit:** 13 September 2026  
**Audited Target:** `Eduboost-V2` (`master` branch @ commit `cb2e62c6d`)  
**Auditor:** Senior Software Architect, Technical Auditor & Security Engineer  
**Audit Standard:** Prime Directive (Absolute Empirical Truth Over Conversational Optimism / Anti-Theatre Enforcement)  
**Execution Environment:** Linux x86_64 / Python 3.12.3 / Node v22.22.3 / pnpm 9.14.4 / PostgreSQL 16 (pgvector) / Redis 7  

---

## 1. Executive Summary & Ground Truth Scorecard

An exhaustive, zero-trust empirical technical audit was conducted across the entire EduBoost V2 codebase. In accordance with the project's governance directive, **no markdown documentation, register claims, or badges were accepted as authoritative**. Every claim was independently investigated against actual Python AST, TypeScript source files, SQL migrations, Docker specifications, and live toolchain executions (compilers, type checkers, linters, security scanners, test runners, and dependency graphs).

### 1.1 Repository Ground Truth Metrics

| Dimension | Measured Value | Repository Location / Verification Command |
| :--- | :--- | :--- |
| **Backend Source Files** | **471** Python files | `find app -name "*.py"` |
| **Total Lines of Python Code** | **70,223** LOC (app only) | Bandit scan metric |
| **Registered API Routes** | **459** route entries (8 ops, 225 duplicated across `/api/v2` & `/v2`) | `scripts/generate_route_inventory.py --check` |
| **Database ORM Models** | **103** mapped tables | `Base.metadata.tables` (`app/models/`) |
| **Alembic Revisions** | **48** migration scripts, **1** linear head (`20260711_1510...`) | `alembic heads` (`alembic/versions/`) |
| **Pytest Total Collected Tests** | **7,455** test items | `pytest --collect-only -q` |
| **Frontend Source Files & Tests** | **44** test files, **149** vitest tests (Next.js 16/React 18) | `pnpm test` (`app/frontend`) |
| **Scripts Ecosystem** | **629** Python scripts (including 168+ `check_*.py` scripts) | `ls scripts/*.py` |
| **Documentation Volume** | **1,952** markdown files | `find docs -name "*.md"` |

---

### 1.2 Ground Truth Scorecard

| Architectural Domain | Declared State (Docs / Register) | Verified Code Reality | Severity / Verdict |
| :--- | :--- | :--- | :--- |
| **Service Layer Isolation** | "Strict isolation; API routers never import repositories" | Routers avoid direct imports, but `app/api_v2_routers/diagnostics.py` imports `diagnostic_repositories` which dynamically instantiates repositories at runtime, circumventing `.importlinter`. | ⚠️ **MEDIUM (Architectural Circumvention)** |
| **Static Typing & Mypy** | "Mypy static type analysis passes cleanly (0 issues in 470 files)" | **95 modules** are suppressed via `ignore_errors = True` in `mypy.ini`. Unsuppressed analysis reveals **56+ real type errors** across 15 core files. | 🛑 **HIGH (False Compliance)** |
| **Code Hygiene & Linters** | "Zero linter violations across app" | `pyproject.toml` broadly ignores `E722`, `F401`, `F841`, `F811`. 8 unused imports exist; loose exception handling is masked. | ⚠️ **MEDIUM (Suppressed Hygiene)** |
| **Security Scanning (Bandit)** | "Zero high/medium security issues" | `scripts/.bandit` has invalid INI syntax that crashes Bandit `-c`. Native scan flags **6 Medium-severity SQL injection warnings** in semantic retrieval. | 🛑 **HIGH (Vulnerability & Broken Tooling)** |
| **Test Coverage** | "95.7% confirmed statement coverage; 90% floor CI-enforced" | CI workflows run only 4 unit tests and 7 integration tests with `--threshold-only` metadata check; no coverage is calculated or enforced in CI. Single unified coverage run fails. | 🛑 **CRITICAL (Compliance Theatre)** |
| **Database Schema Drift** | "Zero schema drift verified" | `alembic/env.py` and comparison scripts explicitly ignore indexes, constraints, types, and 5 consolidation tables. | ⚠️ **MEDIUM (Masked Drift)** |
| **Commercial & Billing Lock** | "Fail-closed lock active (`BILLING_FAIL_CLOSED_LOCK = True`)" | Verified. `assert_billing_authorized` actively blocks live payments (`HTTP 403`) against `true_state_remediation_register.json`. | 🟢 **VERIFIED (Genuine Fail-Closed)** |
| **Pedagogical Integrity (KG)** | "Grade 4 Math KG mapped; mastery capped at 0.6" | Verified. Grade 4 Math graph (226 nodes, 260 edges) exists; `MAX_CONFIDENCE_THRESHOLD = 0.60` strictly raises `MasteryBoundError`. Runtime KG is disabled by default. | 🟢 **VERIFIED (Sound Invariants)** |
| **POPIA / Privacy Cascades** | "Transactional DSR erasure and consent gates enforced" | Consent and erasure gates are present and functional, but code sprawl exists across 6 overlapping POPIA services with dynamic fallback reflection. | ⚠️ **LOW / MEDIUM (Technical Debt)** |
| **Frontend & Offline Build** | "Ready for release standalone frontend build" | Vitest (149 tests) and `tsc` pass, but `pnpm run build` crashes in sandboxed/offline environments due to network-dependent Google Fonts. | 🛑 **HIGH (Build Reliability Blocker)** |

---

## 2. Deep Dive: Architectural Boundaries & Service Layer Isolation

### 2.1 The Dynamic Import Circumvention Pattern
Project rule 4 mandates:
> *Routers (`app/api_v2_routers/*`, `app/modules/*`) must never import directly from repositories (`app/repositories/*`). All data access must route through typed domain services (`app/services/*`). Enforce this via .importlinter and AST checks.*

`.importlinter` enforces:
```ini
[importlinter:contract:api_v2_routers_do_not_import_repositories]
name = FastAPI v2 routers should not import repositories directly
type = forbidden
source_modules = app.api_v2_routers
forbidden_modules = app.repositories
```

**Empirical Finding:**
`.venv/bin/lint-imports` passes with 4 kept contracts. However, inspection of `app/api_v2_routers/diagnostics.py` reveals lines 19, 121, 132, 136, 163, 168:
```python
from app.api_v2_deps import diagnostic_repositories
...
learner = await diagnostic_repositories.learner(db).get_by_id(learner_id)
canonical_items = await diagnostic_repositories.item_bank(db).list_approved_for_grade(learner.grade, limit=20)
diag_repo = diagnostic_repositories.diagnostic(db)
await diagnostic_repositories.learner(db).update_theta(body.learner_id, theta_after)
```
In `app/api_v2_deps/diagnostic_repositories.py`:
```python
_REPOSITORY_TARGETS = {
    "learner": ("app.repositories.repositories.LearnerRepository", ...),
    "guardian": ("app.repositories.repositories.GuardianRepository", ...),
    "irt": ("app.repositories.repositories.IRTRepository", ...),
    ...
}
```
Repositories are dynamically imported at runtime via `importlib.import_module`. The router directly executes data persistence operations, completely bypassing the domain service layer while bypassing static import-linter detection.

### 2.2 Dynamic Reflection in POPIA Consent Lifecycle
In `app/api_v2_deps/consent_lifecycle.py` (lines 15–30, 55–65):
```python
def _load_learner_write_helper():
    candidates = (
        ("app.core.authorization", "require_learner_write_for_current_user"),
        ("app.core.authorization", "require_learner_write"),
        ("app.security.dependencies", "require_learner_write_for_current_user"),
        ("app.security.dependencies", "require_learner_write"),
        ("app.core.dependencies", "require_learner_write_for_current_user"),
        ("app.core.dependencies", "require_learner_write"),
    )
...
async def enforce_popia_learner_write(current_user: Any, learner_id: Any) -> Any:
    helper = _load_learner_write_helper()
    attempts = (((current_user, learner_id), {}), ((learner_id, current_user), {}))
    for args, kwargs in attempts:
        try:
            return await _maybe_await(helper(*args, **kwargs))
        except TypeError:
            continue
```
The application dynamically searches through 6 different module locations and brute-forces argument permutations at request time. This indicates architectural instability and unresolved refactoring debt.

### 2.3 Legacy Quarantine Status
The legacy quarantine rule is **strictly verified**. The directory `app/legacy` does not exist; legacy code has been quarantined to `archive/`. Zero imports from `app.legacy` or `archive` exist in `app/`.

---

## 3. Deep Dive: Static Analysis, Type Safety & Linters

### 3.1 Mypy Type Checking: 95 Blanket Suppressions
Running `mypy app` returns:
```text
Success: no issues found in 470 source files
```
**Empirical Finding:**
This success is manufactured. In `mypy.ini`, **95 modules** are explicitly configured with `ignore_errors = True`. These include:
- `app.api_v2_routers.auth`
- `app.api_v2_routers.billing`
- `app.api_v2_routers.content_factory`
- `app.api_v2_routers.diagnostics`
- `app.api_v2_routers.popia`
- `app.core.database`, `app.core.config`, `app.core.authorization`
- `app.repositories.audit_repository`, `app.repositories.auth_repository`, `app.repositories.learner_repository`
- `app.services.auth_application_service`, `app.services.popia_service`

When `mypy` is executed on `app/api_v2_routers/auth.py` with suppressions removed, it reveals **56 severe type errors** in 15 files:
1. `app/core/config.py:143`: `Name "TENANT_BUDGET_ALERT_PCT" already defined on line 124 [no-redef]` (duplicate configuration declarations).
2. `app/repositories/audit_repository.py:229, 266, 288`: Calling asyncpg driver methods (`.fetchrow()`, `.fetch()`) directly on SQLAlchemy `AsyncSession` objects.
3. `app/repositories/study_plan_repository.py:110-113`: Accessing nonexistent attributes (`subject_code`, `grade_level`, `mastery_score`, `knowledge_gaps`) on `SubjectMastery`.
4. `app/repositories/auth_repository.py:47`: Accessing nonexistent attribute `verification_token` on `Guardian`.
5. `app/repositories/diagnostic_repository.py:27`: Accessing nonexistent attribute `subject` on `DiagnosticSession`.
6. `app/api_v2_routers/auth.py:183`: `AuthContext` object treated as dictionary (`auth.get(...)`).

### 3.2 Ruff Configuration Hygiene
In `pyproject.toml`:
```toml
[tool.ruff.lint]
ignore = [
    "E401", "E402", "E501", "E701", "E702", "E722", "E741",
    "F401", "F402", "F811", "F841", "W291", "W292", "W293"
]
```
`F401` (unused imports), `F841` (unused variables), and `E722` (bare except) are globally suppressed. Testing `app` with `ruff check --select F401` revealed 8 dead imports across production files.

### 3.3 Bandit Security Scanning: Corrupted Configuration & Raw SQL Injections
Running `.venv/bin/bandit -r app -c scripts/.bandit -ll` fails with exit code 2:
```text
[config] ERROR expected '<document start>', but found '<scalar>' in "scripts/.bandit", line 2, column 1
```
`scripts/.bandit` is written in INI format (`[bandit] skips = ...`), whereas modern Bandit requires YAML.
Running Bandit directly without the broken config file flags **6 Medium-severity CWE-89 (SQL Injection) issues**:
- Locations: `app/services/semantic_retrieval/repository.py` (lines 88, 121, 149, 178) and `app/services/semantic_retrieval/indexing.py` (line 296).
- Root Cause: Queries use string interpolation (`f"""SELECT {_COMMON_SELECT} ... WHERE {_FILTER_SQL} ..."""`) with inline `# nosec B608` comments placed inside the multi-line string literals. Bandit does not treat text inside python strings as comments; the suppression fails and raw dynamic SQL fragments remain unvalidated.

---

## 4. Deep Dive: The Coverage Illusion & Test Suite Architecture

### 4.1 Declared Claims vs Verifiable Reality
The repository documentation (`README.md`, `docs/reports/coverage_target_90_completion_report.md`, and `docs/current_state.md`) asserts:
- **Statement Coverage:** ~95.7% across `app/`.
- **Enforcement:** "Strict 90% floor enforced across CI, Makefile, and coverage contracts."

**Empirical Reality:**
1. **CI Does Not Run Coverage:**
   In `.github/workflows/pr-core.yml` and `product-runtime.yml`, the string `COVERAGE_THRESHOLD: "90"` exists in `env:`. However:
   - `pr-core.yml` executes only 4 unit test files in `fast-unit-tests`.
   - `product-runtime.yml` executes only 7 integration test files.
   - `pr-core.yml` runs:
     `python3 scripts/coverage_suites/verify_coverage_contract.py --threshold-only`
     This script only verifies that the string `"90"` in `coverage_contract.json` matches the Makefile and workflow text. **It does not calculate code coverage.**
   - Zero CI jobs run `pytest --cov` or `make test-coverage`.
2. **Actual Single-Run Coverage:**
   The committed `coverage.xml` generated earlier shows:
   - Valid lines: 34,767
   - Covered lines: 2,485
   - Line coverage: **7.15%**
   Running `coverage report` on the existing `.coverage` database yields **5.9%**.
3. **The Layered Calculation Method:**
   In `docs/reports/coverage_target_90_completion_report.md`, the reported 95.7% was achieved by running isolated tests on individual subpackages with targeted flags (e.g. `pytest tests/unit/services/ --cov=app/services`), then summing the arithmetic totals into a Markdown table.
4. **Authenticity of Unit Tests:**
   The unit tests themselves are **genuine, highly detailed, and valid**:
   - `tests/unit/services/` executes **1,472 tests** in 51.08s with **0 failures**, achieving **92.9%** statement coverage on `app/services/`.
   - `tests/unit/routers/` executes **271 tests** in 40.10s with **0 failures**, achieving **97.2%** statement coverage on `app/api_v2_routers/`.
   - `tests/unit/security/` executes **10 tests** in 5.58s with **0 failures**, achieving **100.0%** statement coverage on `app/security/`.
   The issue is not that the unit tests are fake; the issue is that **they have never been unified into a single repeatable CI test run that validates 90% coverage globally across the entire application**.

---

## 5. Deep Dive: API Surface, Routing & Contracts

### 5.1 Route Inventory Verification
Running `python3 scripts/generate_route_inventory.py --check` passes cleanly.
- Total route entries: **459**
- Routing architecture:
  - 8 operational routes: `/`, `/health`, `/ready`, `/metrics`, `/v2/health/deep`, `/api/v2/health/deep`, `/docs`, `/redoc`.
  - 36 feature routers mounted twice via `API_PREFIXES = ("/api/v2", "/v2")` in `app/api_v2.py`.
  - Every feature endpoint has dual identical paths (e.g. `/api/v2/lessons/generate` and `/v2/lessons/generate`).
  - 1 development route: `/__dev/slow_query` (disabled in production).
- OpenAPI specification: `docs/openapi.json` and `docs/openapi.yaml` match code (`generate_openapi.py --check` passes).

---

## 6. Deep Dive: Database, Models & Migration Drift

### 6.1 ORM Table Footprint vs Alembic Migrations
- ORM models in `app/models/` map **103 tables** in `Base.metadata`.
- Alembic head: 1 linear head (`20260711_1510_prd11_runtime_green_exec5`).
- **Schema Drift Suppression:**
  In `alembic/env.py`:
  ```python
  def _include_object(object_, name, type_, reflected, compare_to):
      if type_ == "table" and reflected and compare_to is None:
          return name not in _CONSOLIDATION_TABLES
      if type_ in {"index", "unique_constraint", "foreign_key_constraint"}:
          return False
      return True
  ```
  And in `scripts/compare_orm_tables_to_database.py`:
  An `--ignore-consolidation-tables` parameter explicitly suppresses drift on 5 legacy tables:
  `consent_records`, `correction_requests`, `data_export_requests`, `erasure_requests`, `restriction_requests`.
  These tables were created in early migrations but lack corresponding ORM definitions in `app/models/` (which uses `erasure_request` singular). Database constraints, indexes, and column types are excluded from automated drift detection.

---

## 7. Deep Dive: Security, Cryptography & Authority Boundaries

### 7.1 JWT Validation & Keyring
- Implemented in `app/services/jwt_keyring.py`.
- Supports key IDs (`kid`), symmetric secret rotation, and status tagging (`current`, `previous`).
- `validate_jwt_keyring_environment()` is executed on application startup and raises `JWTKeyringError` if production runs with placeholder secrets (`CHANGE_ME*`, `dev-insecure*`).

### 7.2 Live Billing Fail-Closed Lock
- In `app/services/billing_guard.py`, `assert_billing_authorized()` inspects `docs/roadmap/production_readiness/true_state_remediation_register.json`.
- Registered boundary:
  ```json
  "authority_boundaries": {
    "billing_launch_authorised": false,
    "deployment_authorised": false,
    "live_payment_processing_authorised": false,
    "production_release_authorised": false,
    "public_beta_authorised": false,
    "public_beta_live_traffic_authorised": false,
    "release_tag_authorised": false
  }
  ```
- Any request to `/billing/checkout`, `/billing/portal`, or `/billing/webhook` raises `HTTP 403 Forbidden` with header `X-Billing-Lock: LOCKED_FAIL_CLOSED`.
- **Verdict: Genuine, robust fail-closed lock.**

### 7.3 Compliance Theatre in Verification Scripts
The repository contains 629 scripts in `scripts/`, including over 168 `check_*.py` files. Many checks use trivial substring searches:
- `scripts/check_production_secret_placeholders.py` tests whether literal string `"CHANGE_ME_IN_PRODUCTION_AT_LEAST_32_CHARS"` is in `app/core/config.py`.
- `scripts/check_dev_only_endpoint_exposure.py` tests whether string `"settings.is_production()"` is in `app/api_v2_routers/auth.py`.
- `scripts/check_environment_security_contract.py` tests whether string `"ENVIRONMENT: Literal"` is in `app/core/config.py`.
These scripts pass based on literal code comments and variable names rather than behavioural proofs.

---

## 8. Deep Dive: Pedagogical Integrity & Knowledge Graph

### 8.1 Grade 4 Mathematics CAPS Knowledge Graph
- Data file: `data/knowledge_graph/caps_graph_foundation/grade4_mathematics_caps_graph.json`
- Metrics: **226 nodes**, **260 edges**, **21 topics**, **29 subtopics**, **101 assessment statements**, **68 misconceptions**, **35 prerequisite edges**.
- Graph integrity: Structurally sound and validated against CAPS curriculum requirements.

### 8.2 Mastery Bounds & Mathematical Ceilings
- Implemented in `app/services/mastery_engine.py`.
- Mathematical constant: `MAX_CONFIDENCE_THRESHOLD = 0.60`.
- Invariant guard: `assert_no_authoritative_claims()` raises `MasteryBoundError` if any confidence exceeds `0.60` or if mastery state is declared `AUTHORITATIVE`.
- **Verdict: Genuine educational validity safeguards.**

### 8.3 Runtime KG Execution State
- In `app/services/runtime_kg/feature_flags.py`:
  `enabled: bool = os.getenv("EDUBOOST_RUNTIME_KG_ENABLED", "false")`
- Default state is `false`. When disabled, `build_lesson_context_with_runtime_kg` automatically rolls back to the legacy learner context builder.

---

## 9. Deep Dive: Frontend Quality & Build Integrity

### 9.1 Stack & Test Suite
- Frontend application located in `app/frontend/`.
- Framework: Next.js 16.2.11, React 18.3.1, Tailwind CSS 3.4.3, Zustand 5.0.14.
- TypeScript compilation: `tsc --noEmit` passes with **0 errors**.
- Vitest unit tests: **44 test files, 149 tests pass** in 39.59s.

### 9.2 Offline Build Blocker
Running `pnpm run build` inside a sandboxed/offline container fails with:
```text
Failed to compile.
src/app/layout.tsx
`next/font` error: Failed to fetch `Geist` from Google Fonts.
`next/font` error: Failed to fetch `Geist Mono` from Google Fonts.
> Build failed because of webpack errors
```
`src/app/layout.tsx` imports Google Fonts via `next/font/google`. In offline, airgapped, or restricted CI environments, the Next.js compiler cannot reach `fonts.googleapis.com` and terminates compilation.

---

## 10. Summary of Critical Vulnerabilities, Deficiencies & Technical Debt

| ID | Domain | Category | Description | Recommended Remediation |
| :--- | :--- | :--- | :--- | :--- |
| **DEF-01** | CI / CD | Compliance Theatre | CI does not execute test coverage; `--threshold-only` metadata check masks lack of unified test coverage execution. | Add a real coverage step in CI running `tests/unit` with unified `--cov=app` aggregation. |
| **DEF-02** | Type Safety | False Compliance | 95 modules suppressed in `mypy.ini`, hiding 56+ type errors in auth, database, repositories, and config. | Progressively burn down type errors and remove `ignore_errors = True` per package. |
| **DEF-03** | Security | CWE-89 (SQLi) | Raw string interpolation in semantic retrieval SQL queries; `# nosec` placed inside string literal. | Use SQLAlchemy parameterized bind parameters (`:param`) instead of string interpolation. |
| **DEF-04** | Security | Broken Tooling | `scripts/.bandit` written in INI format causes Bandit `-c` to crash on YAML parsing. | Convert `scripts/.bandit` to standard YAML syntax. |
| **DEF-05** | Architecture | Boundary Violation | `app/api_v2_routers/diagnostics.py` uses dynamic imports to access repositories, circumventing `.importlinter`. | Route all diagnostic data access through `DiagnosticService`. |
| **DEF-06** | Frontend | Build Reliability | `src/app/layout.tsx` fetches Google Fonts at build time, failing in offline sandbox/CI environments. | Switch to self-hosted fonts via `next/font/local` or supply font fallback definitions. |
| **DEF-07** | Database | Schema Blindspot | Index, constraint, and table-name drift suppressed in Alembic and comparison scripts. | Reconcile consolidation tables (`erasure_requests` vs `erasure_request`) in models. |
| **DEF-08** | Code Hygiene | Loose Linters | Broad ignores in `pyproject.toml` (`E722`, `F401`, `F841`, `F811`) hide dead imports and bare exceptions. | Remove broad ignores; enable `F401` and `E722` in Ruff. |

---

## 11. Conclusion & Certification

EduBoost V2 contains **substantial, high-quality engineering work**:
- Over 1,700 rigorously written, passing unit tests across domain services, routers, and security.
- Comprehensive mathematical bounding on educational algorithms (`MAX_CONFIDENCE_THRESHOLD = 0.60`).
- Strict fail-closed commercial and live billing locks.
- Clean OpenAPI and Route Inventory alignment.
- Complete quarantine of legacy code.

However, **the project's declared compliance metrics and documentation do not reflect empirical reality**:
- 90% test coverage is **not enforced or measured in CI**.
- Mypy type-checking clean status is **an artifact of 95 suppressed modules**.
- Bandit security checks are **broken by malformed configuration and fail on semantic retrieval queries**.
- API router isolation is **bypassed via dynamic repository adapter loading**.

Until these empirical deficiencies are remediated, EduBoost V2 cannot truthfully be declared "ready for production release" or "90% covered". The true state of the repository requires focused technical debt burndown rather than further documentation expansion.

*Report signed & sealed in accordance with The Prime Directive: Truth Over Optimism.*
