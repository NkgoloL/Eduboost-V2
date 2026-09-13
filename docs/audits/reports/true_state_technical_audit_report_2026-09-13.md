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
**Codebase, CI/CD, Architecture, Security & Operational Assurance Review**

**Document ID:** `AUDIT-REP-2026-09-13-COMPREHENSIVE-TRUE-STATE`  
**Date of Audit:** 13 September 2026  
**Audited Target:** `Eduboost-V2` (`master` branch @ commit `6a432bd4a` / archive snapshot)  
**Auditors:** Senior Software Architect, Technical Auditor & Security Engineer (Synthesized with Independent Technical Audits of 10 Sep & 13 Sep 2026)  
**Audit Standard:** Prime Directive (Absolute Empirical Truth Over Conversational Optimism / Anti-Theatre Enforcement)  
**Execution Environment:** Linux x86_64 / Python 3.12.3 / Node v22.22.3 / pnpm 9.14.4 / PostgreSQL 16 (pgvector) / Redis 7  

---

## 1. Executive Summary & Ground Truth Scorecard

An exhaustive, zero-trust empirical technical audit was conducted across the entire EduBoost V2 codebase, synthesizing direct runtime investigations with two independent technical audit passes (conducted 10 September and 13 September 2026). In strict adherence to the project's governance directive, **no markdown documentation, register assertions, or CI badges were accepted as authoritative**. Every finding was established directly against Python AST structures, TypeScript source files, SQL migrations, Docker specifications, and live toolchain executions (compilers, type checkers, linters, security scanners, test runners, and dependency graphs).

### 1.1 Repository Ground Truth Metrics

| Dimension | Measured Value | Repository Location / Verification Command |
| :--- | :--- | :--- |
| **Backend Source Files** | **470** Python files | `find app -name "*.py"` |
| **Total Lines of Python Code (App)** | **83,936** LOC (`app/` only) | Line counter (`wc -l` / AST walk) |
| **Test Suite Footprint** | **1,350** files, **160,054** LOC, **7,363** test functions | `grep -E "(def test_|async def test_)" tests/` |
| **Tooling & Governance Scripts** | **1,150** files, **151,148** LOC (including 168+ `check_*.py` scripts) | `find scripts -type f` |
| **Frontend Source Files** | **237** TS/TSX files, **20,745** LOC, **149** vitest tests | `pnpm test` (`app/frontend/`) |
| **Registered API Routes** | **459** route entries (8 ops, 225 duplicated across `/api/v2` & `/v2`) | `scripts/generate_route_inventory.py --check` |
| **Database ORM Models** | **103** mapped tables, 0 name/table collisions | `Base.metadata.tables` (`app/models/`) |
| **Alembic Migration Graph** | **47** active revisions (single root, single head), 4 inert in `_deprecated/` | `alembic heads` (`alembic/versions/`) |
| **Production Runtime Dependencies** | **121** packages in `requirements/base.txt` — **0 known CVEs** | `pip-audit` against PyPI/OSV |
| **Inference Container Dependencies** | **7** packages in `docker/requirements.inference.txt` — **38 unique CVEs** | `pip-audit` against live OSV database |
| **Production Frontend Dependencies** | **311** packages in `pnpm-lock.yaml` — **0 known CVEs** | `pnpm audit --prod` |
| **Documentation Volume** | **1,951** markdown files in `docs/`, **82** in `audits/` | `find docs audits -name "*.md"` |

---

### 1.2 Ground Truth Scorecard

| Architectural Domain | Declared State (Docs / Registers) | Verified Code Reality | Severity / Verdict |
| :--- | :--- | :--- | :--- |
| **CI Test Execution Gate** | "Comprehensive CI test gate certifies full test suite" | CI runs only **70 of 7,363 test functions (≈0.95%)** across 11 hand-picked files. The remaining 99.05% of tests never run in any GitHub Actions PR workflow. | 🛑 **CRITICAL (Assurance Vacuum)** |
| **Test Coverage Reporting** | "95.7% confirmed statement coverage; 90% floor CI-enforced" | CI workflows run **zero coverage calculations**. The "Verify Coverage Threshold Alignment" step merely validates that the string `"90"` appears in config files. Real global single-run coverage is unmeasured in CI. | 🛑 **CRITICAL (Compliance Theatre)** |
| **Inference Service Dependencies** | "Secure and audited supply chain" | `docker/requirements.inference.txt` (used by `Dockerfile.inference`) pins packages with **38 unique known CVEs** (`transformers==4.40.0` has 26 CVEs; `starlette==0.37.2` has 7 CVEs). Excluded from CI `pip-audit`. | 🛑 **HIGH (Live Endpoint Vulnerability)** |
| **Static Typing (Mypy)** | "Type checking passes cleanly across all source files" | `mypy.ini` sets `ignore_errors = True` on **95 modules**, concentrated precisely on auth, JWT keyring, billing/Stripe, POPIA/consent, and repositories. Removing suppressions uncovers **56+ real type errors**. | 🛑 **HIGH (Masked Deficiencies)** |
| **Static Security (Bandit)** | "Zero high/medium security issues in codebase" | Both `/.bandit` and `/scripts/.bandit` have invalid INI formatting causing parser crashes under `-c`, and neither is referenced in CI. Bandit flags **11 B608 sites** (10 sound upon manual audit; 1 un-whitelisted metadata SQL site). | ⚠️ **MEDIUM (Broken Config & Defense Gap)** |
| **Service Layer Isolation** | "Strict architectural boundaries: routers never import repositories" | `app/api_v2_routers/diagnostics.py` imports `diagnostic_repositories`, which dynamically calls `importlib.import_module()` to instantiate repositories at runtime, circumventing `.importlinter`. | ⚠️ **MEDIUM (Architectural Circumvention)** |
| **POPIA / Consent Architecture** | "Unified, transactional consent and DSR engine" | While `data_subject_rights_service.py` is structurally complete, consent logic is fragmented across **22 files** (14 in `app/services/` alone) exhibiting heavy successive adapter/shim layering. | ⚠️ **MEDIUM (Architectural Sprawl)** |
| **Static Analysis (Ruff)** | "Modern code quality and hygiene enforcement" | `pyproject.toml` restricts Ruff to `["E", "F", "W"]` (no bugbear, security, or complexity) and explicitly ignores `E722` (bare except), `F401` (unused imports), and `F841` (unused variables). | ⚠️ **LOW (Permissive Linter Gate)** |
| **Frontend Tooling Alignment** | "Modern frontend stack on Next.js 16" | `next` is 16.3.3, but `eslint-config-next` and `@next/bundle-analyzer` are locked at `15.5.18` (a full major version behind). `next/font/google` causes offline build failures in sandboxed environments. | ⚠️ **LOW (Tooling Drift & Build Fragility)** |
| **Commercial Billing Lock** | "Fail-closed lock active (`BILLING_FAIL_CLOSED_LOCK = True`)" | Verified. `assert_billing_authorized` actively inspects `true_state_remediation_register.json` and returns HTTP 403 on live checkout requests. | 🟢 **VERIFIED (Sound Fail-Closed)** |
| **Pedagogical Invariants (KG)** | "Grade 4 Math KG mapped; mastery capped at 0.60" | Verified. Grade 4 Math graph (226 nodes, 260 edges) is structurally sound; `MAX_CONFIDENCE_THRESHOLD = 0.60` raises `MasteryBoundError`. Runtime KG disabled by default. | 🟢 **VERIFIED (Sound Invariants)** |
| **Database & Migrations** | "Deterministic migrations; zero model collision" | Verified. 103 ORM models match 103 tables with zero collisions. Alembic graph has 1 root and 1 head across 47 active revisions (4 deprecated files inert). | 🟢 **VERIFIED (Technically Sound)** |
| **Secrets Management** | "Active scanning for credentials and API keys" | Verified. `detect-secrets` (879 baselined items) and `gitleaks` are active in CI with scoped rules. Manual regex sweep of `app/` found no un-baselined credentials. | 🟢 **VERIFIED (Mature Tooling)** |

---

## 2. Deep Dive: Testing Pipeline & CI Assurance Realities

### 2.1 The ~0.95% CI Test Execution Gate
The repository contains **7,363 test functions** across 1,350 files (160,054 lines in `tests/`). However, analysis of `.github/workflows/` reveals that GitHub Actions PR workflows execute only a microscopic fraction of these tests:

- **`pr-core.yml` (`fast-unit-tests` job):** Executes only 4 hardcoded test files:
  1. `tests/unit/test_etl_mcp_server_startup.py`
  2. `tests/unit/test_subscription_service.py`
  3. `tests/unit/test_password_policy.py`
  4. `tests/unit/test_popia_consent_versioning.py`
  *(Total: 33 test functions)*
- **`product-runtime.yml` (`runtime-services-integration` job):** Executes only 7 hardcoded test files:
  1. `tests/integration/test_api_envelope.py`
  2. `tests/integration/test_security_headers.py`
  3. `tests/integration/test_v2_routers.py`
  4. `tests/integration/test_deep_health.py`
  5. `tests/integration/test_audit_immutability.py`
  6. `tests/integration/test_diagnostic_session.py`
  7. `tests/integration/test_rate_limits.py`
  *(Total: 37 test functions)*

**Empirical Result:** Across both core CI pipelines, exactly **70 of 7,363 test functions (≈ 0.95%)** are executed on any pull request. Over **99% of the test suite (6,591+ test functions)** is never invoked in automated PR validation.

### 2.2 Analysis of the Three New CI "Coverage" Checks
Recent commits added three new steps to `pr-core.yml`, framed in project documentation as establishing a strict coverage gate. AST and code inspection of these steps reveals:

1. **"Test Import Integrity Audit" (`python3 scripts/audit_test_imports.py`):**
   - AST-walks `tests/test_*.py` files to check that `from app.X import Y` statements reference valid modules/attributes.
   - **Executes zero tests.**
2. **"Pytest Blanket Test Collection Gate" (`python3 -m pytest --collect-only -q`):**
   - Confirms that pytest can gather test items without syntax or module import errors.
   - **Executes zero test bodies or assertions.**
3. **"Verify Coverage Threshold Alignment" (`scripts/coverage_suites/verify_coverage_contract.py --threshold-only`):**
   - Inspects `coverage_contract.json`, `Makefile`, `pr-core.yml`, `pytest-coverage.ini`, and `.coveragerc` via text/regex to confirm that each file contains the string `"90"`.
   - **Executes zero tests and computes zero code coverage.**

A pull request will pass this CI gate with 0% real test coverage, provided all configuration files consistently quote the number 90.

### 2.3 Authenticity of Test Assets vs Execution Gaps
Sampling of the 58 newest test files (representing 702 test functions added across Batches 412–428, such as `tests/unit/modules/test_modules_burndown_complete_batch422.py`) confirms that these are **genuine, substantive unit tests**:
- They employ AsyncMock repository doubles, assert against real domain service return structures, verify audit event side-effects, and target specific statement boundaries.
- They are not superficial "import and assert True" stubs.
- In isolated local test runs, `tests/unit/services/` executes 1,472 tests in 51s with 0 failures, reaching 92.9% coverage on `app/services/`.
- **The Core Deficiency:** The engineering investment in high-quality test authoring is real, but the assurance pipeline that should run these tests and prove regression safety in CI does not execute them.

---

## 3. Deep Dive: Supply Chain, Security & Vulnerabilities

### 3.1 Inference Service Container Exposure (38 Unique CVEs)
While `requirements/base.txt` (121 production packages) and `app/frontend/pnpm-lock.yaml` (311 packages) have **zero known CVEs**, `docker/requirements.inference.txt` (which builds `Dockerfile.inference` for live ML inference serving) contains severe vulnerabilities:

| Package | Pinned Version | Vulnerability Count | Primary Advisory / Exposure |
| :--- | :--- | :--- | :--- |
| `transformers` | `4.40.0` | **26 unique CVEs** | Multiple arbitrary code execution and deserialization vulnerabilities (fixed in 4.48.0+). |
| `starlette` | `0.37.2` | **7 unique CVEs** | DoS and multipart parser vulnerabilities in the ASGI framework directly fronting HTTP traffic (fixed in 0.40.0+). |
| `torch` | `2.2.0` | **1 CVE** | Memory corruption / DoS issue. |
| `sentencepiece`, `accelerate`, `python-dotenv`, `setuptools` | Various | **1 CVE each** | Tooling and utility vulnerabilities. |

**CI Supply Chain Gap:** In `.github/workflows/security-supply-chain.yml`, the `pip-audit-dependencies` job explicitly scans only:
```bash
pip-audit -r requirements/base.txt -r requirements/dev.txt
```
Neither `docker/requirements.inference.txt` nor `requirements/ml.txt` (48 unique CVEs in offline training dependencies) is included in the CI audit scope. Consequently, high-severity CVEs in the network-facing inference container are completely invisible to automated CI gates.

### 3.2 Bandit Security Tooling & B608 SQL Injection Audit
1. **Broken Configuration:** Both `/.bandit` and `/scripts/.bandit` contain identical skip lists in legacy INI format (`[bandit] skips = B101,...`). Running `bandit -c .bandit` fails with YAML parse errors. Furthermore, the CI invocation in `security-supply-chain.yml` (`python3 -m bandit -r app scripts -ll -q`) omits `-c .bandit` entirely. Both configuration files are completely non-functional.
2. **Detailed Review of 11 B608 Findings:**
   - **Semantic Retrieval (6 sites in `indexing.py` and `repository.py`):** Bandit flags these with LOW confidence because f-strings construct SQL queries. Code-level audit reveals that the interpolated string creates dynamically named SQLAlchemy bind parameters (`:chunk_id_0`, `:chunk_id_1`) for variable-length `IN (...)` clauses, while actual values are bound separately via the params dictionary. This is safe, standard SQLAlchemy usage.
   - **ETL Pipelines (4 sites):** Sound. Queries interpolate fixed literal clauses or validate column names against hardcoded allowed sets.
   - **ETL Metadata Normalization (1 site in `etl_pipeline.py:1140`):** In `normalize()`, column names originate from `infer_metadata()` dictionary keys and are interpolated directly into `UPDATE` statements without an explicit allowlist check at the point of SQL construction. While currently safe because keys are fixed literals, this is a defense-in-depth gap compared to `etl_pipeline_v2.py:434` (which enforces an explicit allowed set).

---

## 4. Deep Dive: Architecture, Static Typing & Code Hygiene

### 4.1 Mypy Type Checking: 95 Blanket Suppressions
Running `mypy app` reports `Success: no issues found in 470 source files`. However, `mypy.ini` declares `ignore_errors = True` across **95 application modules**. The suppressed surface covers the platform's most critical paths:
- **Authentication & Authorization:** `app/api_v2_routers/auth.py`, `auth_extended.py`, `app/core/authorization.py`, `app/services/auth_service.py`, `jwt_keyring.py`.
- **Billing & Payments:** `app/api_v2_routers/billing.py`, `app/core/stripe_client.py`.
- **Compliance & Privacy:** `app/api_v2_routers/popia.py`, `app/services/popia_service.py`, `data_subject_rights_service.py`.
- **Persistence Foundation:** `app/core/database.py`, `app/repositories/base.py`, `auth_repository.py`, `audit_repository.py`.

Evaluating unsuppressed modules in a fully-configured environment reveals **56+ real type errors**, including asyncpg driver calls on SQLAlchemy `AsyncSession` instances, nonexistent attributes accessed on ORM models, and duplicate settings variables.

### 4.2 Dynamic Import Circumvention of `.importlinter`
Project architecture strictly forbids API routers from importing repository modules directly:
```ini
[importlinter:contract:api_v2_routers_do_not_import_repositories]
source_modules = app.api_v2_routers
forbidden_modules = app.repositories
```
**Circumvention:** In [app/api_v2_routers/diagnostics.py](file:///home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/app/api_v2_routers/diagnostics.py) (line 19), the router imports `app.api_v2_deps.diagnostic_repositories`. That helper uses `importlib.import_module()` to dynamically instantiate repository classes at runtime:
```python
_REPOSITORY_TARGETS = {
    "learner": ("app.repositories.repositories.LearnerRepository", ...),
    ...
}
```
The router then executes persistence operations directly (`diagnostic_repositories.learner(db).update_theta(...)`). Because `import-linter` inspects static AST import statements, dynamic runtime imports evade detection completely.

### 4.3 Consent / POPIA Architecture Sprawl
A search across `app/` identifies **22 files** dedicated to consent and POPIA logic, with 14 in `app/services/` alone:
- `consent.py`, `consent_compat.py`, `consent_expiry_service.py`, `consent_renewal_service.py`, `consent_runtime_compatibility.py`, `consent_runtime_orchestrator.py`, `consent_service.py`, `first_consent_runtime_wiring.py`, `popia_consent_lifecycle_adapter.py`, `popia_dsr_service.py`, `popia_erasure_safety.py`, `popia_service.py`, `popia_transactional_lifecycle.py`, `runtime_consent_facade.py`.

While `data_subject_rights_service.py` provides structurally complete handlers for data access, export, erasure, rectification, and SLA tracking, the presence of successive compatibility adapters (`compat`, `runtime_compatibility`, `adapter`, `facade`) points to significant architectural accretion that increases the maintenance and audit surface.

### 4.4 Static Analysis Permissiveness (Ruff)
In `pyproject.toml`, Ruff configuration is restricted:
- Only selects `["E", "F", "W"]` (pycodestyle and Pyflakes).
- Omits `B` (flake8-bugbear), `S` (security), `C90` (mccabe complexity), and `UP` (pyupgrade).
- Explicitly ignores `E722` (bare except), `F401` (unused import), `F811` (redefinition), and `F841` (unused variable).
Consequently, dead code and bare exception handling (`try: ... except: pass`) are invisible to CI linting.

### 4.5 Tooling-to-Product Code Inversion
A language-aware analysis of repository composition shows:
- `scripts/`: **151,148 LOC across 1,150 files**
- `app/`: **83,936 LOC across 470 files**
Governance and verification tooling is **80% larger by LOC and 144% larger by file count** than the product application code it governs. Maintaining this large volume of custom verification scripts carries a substantial maintenance burden.

---

## 5. Verified & Sound Architectural Controls

The audit independently verified that several core structural and security safeguards are genuinely operational and sound:

1. **Commercial & Billing Fail-Closed Lock:** `assert_billing_authorized()` in `app/services/billing_guard.py` inspects `true_state_remediation_register.json` and raises `HTTP 403 Forbidden` (`X-Billing-Lock: LOCKED_FAIL_CLOSED`) on live checkout initialization.
2. **Pedagogical Invariants:** In `app/services/mastery_engine.py`, `assert_no_authoritative_claims()` strictly raises `MasteryBoundError` if learner confidence exceeds `0.60` or if mastery is tagged `AUTHORITATIVE`. The Grade 4 CAPS Math Knowledge Graph (226 nodes, 260 edges) is structurally complete.
3. **Database & Migrations:** 103 ORM models match 103 database tables with zero collisions. Alembic migrations form a clean, single-head sequence across 47 active revisions.
4. **Production API & Frontend Dependencies:** Both `requirements/base.txt` (121 packages) and `app/frontend/pnpm-lock.yaml` (311 packages) carry zero known CVEs.
5. **Secrets Hygiene:** Active CI scanning via `detect-secrets` and `gitleaks` enforces credential boundaries, with 879 approved test tokens and high-entropy fixtures cleanly baselined.
6. **Legacy Isolation:** `app/legacy` has been completely eliminated, and legacy code remains cleanly quarantined in `archive/`.

---

## 6. Deficiency Matrix & Actionable Remediation Plan

| ID | Domain | Severity | Nature of Deficiency | Concrete Remediation Action |
| :--- | :--- | :--- | :--- | :--- |
| **DEF-01** | Dependencies | 🛑 **HIGH** | Inference container (`docker/requirements.inference.txt`) pins 38 unique CVEs (`transformers==4.40.0`, `starlette==0.37.2`). Excluded from CI `pip-audit`. | Upgrade `transformers` (≥4.48.0) and `starlette` (≥0.40.0) in inference requirements; add `docker/requirements.inference.txt` to CI `security-supply-chain.yml`. |
| **DEF-02** | Testing / CI | 🛑 **HIGH** | PR CI workflows execute only 70 of 7,363 test functions (≈0.95%) across 11 hardcoded files. | Replace the four-file list in `pr-core.yml` with `make test-fast` (running all unit tests under marker exclusions); add a scheduled run for integration tests. |
| **DEF-03** | Testing / CI | 🛑 **HIGH** | CI coverage gate verifies configuration string `"90"` via regex rather than executing tests or measuring code coverage. | Wire `make test-coverage` into CI with genuine `--cov=app --fail-under=90` enforcement across executed test suites. |
| **DEF-04** | Type Safety | 🛑 **HIGH** | `mypy.ini` suppresses 95 modules (`ignore_errors = True`), hiding 56+ type errors in auth, billing, POPIA, and database layers. | Progressively burn down type errors module by module, starting with `app/core/` and `app/api_v2_routers/auth.py`, replacing blanket ignore with targeted `# type: ignore[code]`. |
| **DEF-05** | Security | ⚠️ **MEDIUM** | Both `/.bandit` and `/scripts/.bandit` contain broken INI syntax crashing `bandit -c`, and neither is wired into CI. | Convert `scripts/.bandit` to valid YAML syntax; pass `-c scripts/.bandit` in `.github/workflows/security-supply-chain.yml`. |
| **DEF-06** | Architecture | ⚠️ **MEDIUM** | `app/api_v2_routers/diagnostics.py` uses dynamic `importlib` calls to access repositories, circumventing `.importlinter`. | Refactor `diagnostics.py` to interact exclusively with a domain service (`DiagnosticDomainService`). |
| **DEF-07** | Architecture | ⚠️ **MEDIUM** | Consent/POPIA logic is fragmented across 22 files (14 in `app/services/`) with multiple adapter and compatibility shims. | Consolidate consent services into a single authoritative lifecycle path; deprecate redundant compatibility adapters. |
| **DEF-08** | Security | ⚠️ **LOW** | `etl_pipeline.py:1140` (`normalize()`) interpolates metadata dict keys into SQL without an explicit column whitelist. | Add an explicit column allowlist to `normalize()` matching the pattern in `etl_pipeline_v2.py:434`. |
| **DEF-09** | Static Analysis | ⚠️ **LOW** | Ruff rule selection is restricted to `["E", "F", "W"]` while ignoring bare excepts (`E722`) and dead code (`F401`, `F841`). | Enable `flake8-bugbear` (`B`) in `pyproject.toml`; remove broad ignores for `E722` and `F401`. |
| **DEF-10** | Frontend | ⚠️ **LOW** | `eslint-config-next` and `@next/bundle-analyzer` are pinned to 15.5.18, a major version behind `next` (16.3.3). | Bump `eslint-config-next` and `@next/bundle-analyzer` to 16.x-compatible versions. |
| **DEF-11** | Frontend | ⚠️ **LOW** | `src/app/layout.tsx` imports Google Fonts via CDN, causing build crashes in network-isolated environments. | Replace CDN font loading with self-hosted fonts via `next/font/local` or supply offline fallbacks. |
| **DEF-12** | Database | ⚠️ **LOW** | Alembic and comparison scripts explicitly suppress drift on legacy consolidation tables (`erasure_requests`, etc.). | Reconcile model definitions with consolidation tables and eliminate drift suppression rules. |

---

## 7. Conclusion & Governance Certification

This comprehensive audit synthesizes live repository analysis with independent audit evaluations from 10 September and 13 September 2026. The empirical picture is definitive:

1. **Substantive Engineering Core:** The core database models, migration sequence, API route structure, billing fail-closed lock, knowledge graph bounds, and individual unit test suites are well-engineered, authentic, and technically sound.
2. **Assurance Pipeline Disconnect:** The critical vulnerabilities and risks reside not in algorithmic design, but in the **assurance and verification pipeline**:
   - Automated PR CI tests only **0.95%** of the codebase's test functions.
   - The CI coverage gate validates **configuration text, not test outcomes**.
   - Network-facing inference container dependencies carry **38 unique CVEs** that are omitted from CI vulnerability scans.
   - Static type checking is **disabled across 95 high-risk modules**.
   - Architectural isolation is **bypassed via dynamic reflection**.

Until these empirical deficiencies are remediated through genuine code changes and CI gate updates, EduBoost V2 cannot truthfully be certified as "ready for production release" or "90% covered". Remediation must prioritize pipeline realism and technical debt burndown over additional documentation generation.

*Report signed & sealed in accordance with The Prime Directive: Truth Over Optimism.*
