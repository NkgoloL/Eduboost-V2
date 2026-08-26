# Coverage Debt Management and Recovery System

Maps the coverage debt management system from configuration through measurement, tracking, risk classification, and recovery planning. Key configuration at [1a], timeout fix at [1b], CI enforcement at [2b], baseline measurement at [3b], module risk classification at [4b-4d], and recovery sprint plan at [5b-5d].

## Trace ID: 1
**Title:** Coverage Configuration and Timeout Resolution

**Description:** Configuration system that enables async-aware coverage measurement, resolving the timeout blocker that prevented full-suite coverage runs.

**Motivation:**
EduBoost V2 implements an async-aware coverage configuration system to resolve a critical timeout blocker that prevented full-suite coverage runs. The system uses pytest-cov with .coveragerc configuration to enable async concurrency tracing (greenlet, thread), which is essential for accurately measuring coverage in async SQLAlchemy operations. The previous configuration lacked async support, causing 60-second timeouts during coverage runs. The fix adds `concurrency = greenlet,thread` to .coveragerc, enabling proper tracing of async code paths. This configuration establishes the foundation for comprehensive coverage measurement, enabling the team to establish an authoritative baseline (57.5%) and identify coverage debt across the codebase.

**Details:**
- **Execution Flow:** Configuration Files (.coveragerc with concurrency = greenlet,thread, source = app, pytest.ini with --cov=app, --cov-fail-under=80) → Test Execution (pytest runs with coverage enabled, Uses .coveragerc settings, Applies async-aware tracing) → Results Documentation (docs/engineering/coverage_debt.md with Smoke: 32 passed in 80.89s, Full: 2,252 passed, 57.5%)
- **Concurrency Safety:** Coverage measurement is read-only and thread-safe. Async concurrency tracing uses greenlet/thread mode for accurate async code coverage. No distributed locks needed as coverage runs are isolated. Multiple coverage runs can run concurrently on different branches
- **Covered Objects:** .coveragerc configuration, pytest.ini configuration, pytest-cov plugin, Async concurrency tracing, Coverage source scope (app/), Test execution results, Coverage reports (term, HTML, XML)
- **Timeouts:** Configuration loading: <1ms. Coverage tracing per test: ~10-50ms. Smoke tests: ~80s. Full suite: ~35min. Previous timeout: 60s (before fix)
- **Migration Path:** From blocking timeout to async-aware coverage. Migration requires: 1) Add .coveragerc with concurrency settings, 2) Update pytest.ini with coverage options, 3) Verify async code tracing, 4) Run full-suite coverage, 5) Establish baseline
- **Error Handling:** Invalid configuration fails pytest. Timeout failures indicate missing async support. Coverage measurement failures logged. All errors documented in coverage reports
- **Security Considerations:** Coverage measurement is read-only (no code execution). Configuration files in repository. No secrets in configuration. Coverage reports may contain code snippets (internal only)

**Trace text diagram:**
```
Coverage Configuration & Timeout Resolution
├── Configuration Files
│   ├── .coveragerc <-- .coveragerc:1
│   │   ├── concurrency = greenlet,thread <-- 1a
│   │   └── source = app <-- 1b
│   └── pytest.ini <-- pytest.ini:9
│       ├── --cov=app <-- 1c
│       └── --cov-fail-under=80 <-- 1d
├── Test Execution
│   └── pytest runs with coverage enabled
│       ├── Uses .coveragerc settings
│       └── Applies async-aware tracing
└── Results Documentation
    └── docs/engineering/coverage_debt.md <-- coverage_debt.md:25
        ├── Smoke: 32 passed in 80.89s <-- 1e
        └── Full: 2,252 passed, 57.5% <-- 1f
```

**Location ID: 1a**
- **Title:** Async concurrency configuration
- **Description:** Critical fix that resolved 60s timeout by enabling async-aware coverage tracing for SQLAlchemy tests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.coveragerc:3

**Location ID: 1b**
- **Title:** Coverage source scope
- **Description:** Defines app/ as the coverage measurement target, excluding tests and external dependencies
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.coveragerc:5

**Location ID: 1c**
- **Title:** Pytest coverage integration
- **Description:** Pytest default option that activates coverage measurement for all test runs
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:21

**Location ID: 1d**
- **Title:** Local coverage threshold
- **Description:** Local pytest threshold set to 80%, stricter than CI's 60% to encourage higher quality
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:25

**Location ID: 1e**
- **Title:** Timeout resolution evidence
- **Description:** After .coveragerc fix, smoke tests complete in 81s vs previous 60s timeout
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:61

**Location ID: 1f**
- **Title:** Full suite baseline established
- **Description:** Complete coverage run now possible, establishing authoritative 57.5% baseline
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:62

### AI Guide: Coverage Configuration and Timeout Resolution

**Motivation:**
The coverage configuration system enables async-aware coverage measurement, resolving a critical timeout blocker. The .coveragerc configuration with async concurrency support enables full-suite coverage runs by properly tracing async code.

**Details:**

**Async Concurrency and Source Scope**
Async concurrency is a critical fix adding `concurrency = greenlet,thread` to enable async code tracing and resolve the 60s timeout [1a]. The source scope defines app/ as the coverage target, excluding tests and dependencies to focus on production code [1b].

**Pytest Integration**
Pytest integration uses --cov=app to activate coverage and --cov-fail-under=80 to enforce the local threshold, which is stricter than CI [1c][1d]. Test execution uses .coveragerc settings to apply async-aware tracing and generate coverage reports.

**Results Documentation**
Results documentation establishes baselines: smoke tests show 32 passed in 81s, and the full suite shows 2,252 passed with 57.5% coverage [1e][1f]. This provides a baseline for measuring progress toward coverage goals.

## Trace ID: 2
**Title:** CI Coverage Threshold Enforcement

**Description:** CI/CD pipeline enforcement of coverage thresholds, showing the gap between 60% target and 57.5% actual coverage.

**Motivation:**
EduBoost V2 implements CI coverage threshold enforcement to maintain code quality standards and prevent coverage regression. The CI/CD pipeline uses a 60% coverage threshold (COVERAGE_THRESHOLD environment variable) enforced via pytest's --cov-fail-under flag. This gate prevents merging PRs that would reduce coverage below the threshold. The system identified a 2.5% gap between actual coverage (57.5%) and required threshold (60%), triggering a recovery strategy decision. The team chose to maintain the 60% threshold and close the gap through targeted test additions (quick-wins) rather than lowering the threshold, ensuring quality standards are upheld while providing a clear path to compliance.

**Details:**
- **Execution Flow:** Environment Configuration (COVERAGE_THRESHOLD: "60") → Unit Tests Job (pytest tests/ with --cov-fail-under=$COVERAGE_THRESHOLD, Upload coverage to Codecov) → V2 Module Coverage Job (pytest tests/unit/ with --cov=app.api_v2, --cov=app.repositories, --cov=app.services, --cov-fail-under=$COVERAGE_THRESHOLD, Coverage gate enforcement) → Coverage Gap Analysis (Actual: 57.5% < Required: 60%, Recovery Strategy Decision with Option 1: Lower threshold to 55%, Option 2: Add 2.5% via quick-wins)
- **Concurrency Safety:** CI jobs run in isolated containers. Coverage measurement is read-only. Threshold enforcement is deterministic. No distributed locks needed as CI provides isolation. Multiple PRs can run concurrently
- **Covered Objects:** CI/CD pipeline (ci-cd.yml), COVERAGE_THRESHOLD environment variable, pytest --cov-fail-under flag, Codecov integration, V2 module coverage gate, Coverage gap analysis, Recovery strategy
- **Timeouts:** Unit tests: ~5-10min. V2 module tests: ~5-10min. Coverage upload: ~1-2min. Total CI run: ~15-30min
- **Migration Path:** From no coverage enforcement to CI gates. Migration requires: 1) Add COVERAGE_THRESHOLD to CI, 2) Add --cov-fail-under to pytest, 3) Integrate Codecov, 4) Add module-specific gates, 5) Document recovery strategy
- **Error Handling:** Coverage below threshold fails CI. Upload failures logged but don't block. Configuration errors fail CI. All errors logged in CI output
- **Security Considerations:** Threshold from environment (not in code). Coverage reports uploaded to Codecov. No secrets in coverage data. Gate enforcement prevents regression

**Trace text diagram:**
```
CI Coverage Enforcement Pipeline
├── Environment Configuration <-- ci-cd.yml:11
│   └── COVERAGE_THRESHOLD: "60" <-- 2a
├── Unit Tests Job <-- ci-cd.yml:136
│   ├── pytest tests/ <-- ci-cd.yml:152
│   │   └── --cov-fail-under=$COVERAGE_THRESHOLD <-- 2b
│   └── Upload coverage to Codecov <-- ci-cd.yml:160
├── V2 Module Coverage Job <-- ci-cd.yml:230
│   ├── pytest tests/unit/ <-- ci-cd.yml:282
│   │   ├── --cov=app.api_v2 <-- ci-cd.yml:283
│   │   ├── --cov=app.repositories <-- ci-cd.yml:284
│   │   ├── --cov=app.services <-- ci-cd.yml:285
│   │   └── --cov-fail-under=$COVERAGE_THRESHOLD <-- 2c
│   └── Coverage gate enforcement
└── Coverage Gap Analysis
    ├── Actual: 57.5% < Required: 60% <-- 2d
    └── Recovery Strategy Decision <-- 2e
        ├── Option 1: Lower threshold to 55% <-- coverage_baseline_20260527.md:185
        └── Option 2: Add 2.5% via quick-wins <-- coverage_baseline_20260527.md:186
```

**Location ID: 2a**
- **Title:** CI coverage threshold definition
- **Description:** Environment variable defining 60% as the minimum acceptable coverage for CI gates
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:13

**Location ID: 2b**
- **Title:** Unit test coverage enforcement
- **Description:** Pytest invocation with --cov-fail-under flag that fails the build if coverage drops below 60%
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:156

**Location ID: 2c**
- **Title:** V2 module coverage enforcement
- **Description:** Separate coverage gate for V2 modules (api_v2, repositories, services, domain)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:288

**Location ID: 2d**
- **Title:** Coverage gap identified
- **Description:** Documentation of 2.5% gap between actual (57.5%) and required (60%) coverage
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/audits/coverage/coverage_baseline_20260527.md:183

**Location ID: 2e**
- **Title:** Recovery strategy decision
- **Description:** Decision to maintain 60% threshold and close gap through targeted test additions
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/audits/coverage/coverage_baseline_20260527.md:186

### AI Guide: CI Coverage Threshold Enforcement

**Motivation:**
The CI coverage threshold enforcement system maintains code quality standards through automated gates. The CI pipeline enforces coverage thresholds and handles coverage gaps by using environment variables for configurable thresholds and uploading to Codecov for tracking.

**Details:**

**Threshold Configuration**
The threshold configuration uses the COVERAGE_THRESHOLD environment variable, set to 60% in CI and configurable per environment [2a]. This allows different thresholds for different environments while maintaining quality standards.

**Test Gates**
The unit test gate uses pytest with --cov-fail-under to fail the build if below threshold and uploads to Codecov [2b]. The V2 module gate is a separate gate for V2 modules that tests api_v2, repositories, services, and domain with the same threshold enforcement [2c].

**Gap Analysis and Recovery**
Gap analysis identifies the 2.5% gap (57.5% vs 60%), documents it in the coverage baseline, and triggers the recovery strategy [2d]. The recovery strategy offers Option 1 (lower threshold to 55%) or Option 2 (add 2.5% via quick-wins), with Option 2 chosen for quality [2e].

## Trace ID: 3
**Title:** Coverage Baseline Measurement and Module Breakdown

**Description:** Full-suite coverage measurement results showing per-module coverage percentages, from highest (98.1% models) to lowest (38.7% routers).

**Motivation:**
EduBoost V2 implements comprehensive coverage baseline measurement to establish an authoritative understanding of code coverage across all modules. The full-suite coverage run (2,252 tests in 35:15) provides per-module breakdown, identifying high-coverage modules (models at 98.1%, security at 94.0%) and low-coverage modules (routers at 38.7%, repositories at 41.5%). This baseline enables targeted improvement efforts by highlighting coverage debt in critical areas. The measurement covers 45,152 executable lines across 13 packages, providing a complete picture of the codebase. The baseline serves as the foundation for risk classification, prioritization, and recovery planning, ensuring resources are focused on the most impactful areas.

**Details:**
- **Execution Flow:** Full Test Suite Execution (pytest tests/ --cov=app invocation with 2,252 tests pass in 35:15, Coverage: 57.5% baseline, Coverage Report Generation with Per-module breakdown output) → High Coverage Modules (>90%) (app.models: 859 lines, 98.1%) → Medium Coverage Modules (50-80%) (app.modules: 6,577 lines, 70.8%, app.services: 8,498 lines, 53.9%) → Low Coverage Modules (<50%) (app.repositories: 945 lines, 41.5%, app.api_v2_routers: 2,003 lines, 38.7% with Critical gap: auth & POPIA routers)
- **Concurrency Safety:** Coverage measurement is read-only and thread-safe. Test execution is isolated per test. No distributed locks needed as runs are isolated. Multiple baseline runs can run concurrently
- **Covered Objects:** Full test suite (2,252 tests), Coverage baseline (57.5%), Per-module breakdown, High coverage modules (models, security), Medium coverage modules (modules, services), Low coverage modules (repositories, routers), 45,152 executable lines
- **Timeouts:** Full suite execution: ~35min. Report generation: ~1-2min. Total baseline measurement: ~35-37min
- **Migration Path:** From no baseline to comprehensive measurement. Migration requires: 1) Run full-suite coverage, 2) Generate per-module breakdown, 3) Document results, 4) Identify high/medium/low coverage, 5) Establish as baseline
- **Error Handling:** Test failures logged but don't block coverage. Coverage measurement failures logged. Report generation failures logged. All errors documented in coverage reports
- **Security Considerations:** Coverage measurement is read-only. Reports may contain code snippets (internal only). No secrets in coverage data. Baseline data stored in documentation

**Trace text diagram:**
```
Coverage Baseline Measurement System
├── Full Test Suite Execution
│   ├── pytest tests/ --cov=app invocation <-- pytest.ini:21
│   │   ├── 2,252 tests pass in 35:15 <-- 3a
│   │   └── Coverage: 57.5% baseline <-- 3b
│   └── Coverage Report Generation
│       └── Per-module breakdown output <-- coverage_baseline_20260527.md:146
├── High Coverage Modules (>90%)
│   └── app.models: 859 lines, 98.1% <-- 3c
├── Medium Coverage Modules (50-80%)
│   ├── app.modules: 6,577 lines, 70.8% <-- 3d
│   └── app.services: 8,498 lines, 53.9% <-- 3e
└── Low Coverage Modules (<50%)
    ├── app.repositories: 945 lines, 41.5% <-- 3f
    └── app.api_v2_routers: 2,003 lines, 38.7% <-- 3g
        └── Critical gap: auth & POPIA routers <-- coverage_debt.md:74
```

**Location ID: 3a**
- **Title:** Full suite execution results
- **Description:** Complete test suite execution with 2,252 passing tests over 35 minutes
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/audits/coverage/coverage_baseline_20260527.md:127

**Location ID: 3b**
- **Title:** Authoritative baseline coverage
- **Description:** Established 57.5% as the authoritative baseline for 45,152 executable lines
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/audits/coverage/coverage_baseline_20260527.md:128

**Location ID: 3c**
- **Title:** Highest coverage module
- **Description:** Models achieve 98.1% coverage through comprehensive ORM and schema validation tests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/audits/coverage/coverage_baseline_20260527.md:148

**Location ID: 3d**
- **Title:** Modules package coverage
- **Description:** Business logic modules at 70.8%, including lessons, consent, gamification
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/audits/coverage/coverage_baseline_20260527.md:153

**Location ID: 3e**
- **Title:** Services layer coverage
- **Description:** Largest package at 8,498 lines with 53.9% coverage, includes auth, content factory, ETL
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/audits/coverage/coverage_baseline_20260527.md:155

**Location ID: 3f**
- **Title:** Repository layer coverage
- **Description:** Data access layer at 41.5%, tested via integration but lacking direct unit tests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/audits/coverage/coverage_baseline_20260527.md:158

**Location ID: 3g**
- **Title:** Lowest coverage module
- **Description:** API routers at 38.7%, critical gap for auth and POPIA endpoints
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/audits/coverage/coverage_baseline_20260527.md:159

### AI Guide: Coverage Baseline Measurement and Module Breakdown

**Motivation:**
The coverage baseline measurement system establishes an authoritative understanding of code coverage across all modules. The full-suite run provides per-module breakdown for targeted improvement by identifying high, medium, and low coverage areas.

**Details:**

**Full Suite Execution**
Full suite execution runs 2,252 tests in 35:15 with 57.5% baseline coverage across 45,152 executable lines, providing an authoritative measurement [3a][3b]. This establishes the baseline for all future coverage improvements.

**Coverage Levels**
High coverage shows models at 98.1% with comprehensive ORM tests, schema validation, and a well-covered foundation [3c]. Medium coverage includes modules at 70.8% (business logic) and services at 53.9% (largest package), showing room for improvement [3d][3e]. Low coverage includes repositories at 41.5% (data access) and routers at 38.7% (API layer), identifying critical gaps [3f][3g].

**Module Breakdown**
The module breakdown provides per-module percentages and lines of code per module to identify coverage debt and enable prioritization. This allows the team to focus improvement efforts on the most critical gaps.

## Trace ID: 4
**Title:** Module Risk Classification and Priority Assignment

**Description:** Risk classification system assigning P0/P1/P2 priorities based on criticality and coverage gaps, identifying high-risk P0 modules.

**Motivation:**
EduBoost V2 implements a risk classification system to prioritize coverage improvement efforts based on module criticality and coverage gaps. The system assigns P0 (critical security/legal), P1 (core product), and P2 (nice-to-have) priorities, further classified by coverage risk (high, medium, low). This matrix ensures resources are focused on the most impactful areas: P0 high-risk modules (auth router at 38.7%, POPIA router at 38.7%) are prioritized for Sprint 2-3, while P1 medium-risk modules (repositories at 41.5%, services at 53.9%) are scheduled for Sprint 4-5. The classification balances security/legal requirements with product needs, ensuring compliance-critical code is addressed first while maintaining product quality.

**Details:**
- **Execution Flow:** Coverage Baseline Data (57.5%) with app.security: 94.0% coverage, app.api_v2_routers.auth: 38.7%, app.api_v2_routers.popia: 38.7%, app.services.jwt_keyring: 53.9%, app.repositories: 41.5% → Risk Classification Matrix with P0 Modules (Critical Security/Legal) including Security (Low Risk) → Sprint 2, Auth Router (High Risk) → Sprint 2, POPIA Router (High Risk) → Sprint 3, JWT Keyring (Medium Risk) → Sprint 2, and P1 Modules (Core Product) including Repositories (Medium Risk) → Sprint 5, Services (Medium Risk) → Sprint 4, Content Factory → Sprint 4
- **Concurrency Safety:** Classification is stateless and deterministic. No shared state between classifications. No locks needed as operations are read-only. Multiple classifications can run concurrently
- **Covered Objects:** Coverage baseline data, Module criticality (P0/P1/P2), Coverage risk (high/medium/low), Risk classification matrix, Sprint assignments, Priority assignments
- **Timeouts:** Data analysis: ~1-5min. Classification: ~1-5min. Sprint planning: ~5-10min. Total classification: ~5-20min
- **Migration Path:** From ad-hoc prioritization to systematic classification. Migration requires: 1) Define criticality levels, 2) Define risk levels, 3) Create classification matrix, 4) Assign priorities, 5) Schedule sprints
- **Error Handling:** Missing coverage data logged. Classification conflicts resolved manually. Sprint conflicts resolved manually. All errors documented in classification matrix
- **Security Considerations:** P0 priority for security/legal modules. High-risk classification for auth/POPIA. Sprint 2-3 for critical gaps. Ensures compliance-critical code addressed first

**Trace text diagram:**
```
Coverage Debt Management System
└── Module Risk Classification Process
    ├── Coverage Baseline Data (57.5%) <-- coverage_baseline_20260527.md:128
    │   ├── app.security: 94.0% coverage <-- 4a
    │   ├── app.api_v2_routers.auth: 38.7% <-- 4b
    │   ├── app.api_v2_routers.popia: 38.7% <-- 4c
    │   ├── app.services.jwt_keyring: 53.9% <-- 4d
    │   └── app.repositories: 41.5% <-- 4e
    │
    └── Risk Classification Matrix <-- coverage_debt.md:66
        ├── P0 Modules (Critical Security/Legal) <-- coverage_debt.md:70
        │   ├── Security (Low Risk) → Sprint 2 <-- coverage_debt.md:117
        │   ├── Auth Router (High Risk) → Sprint 2 <-- coverage_debt.md:122
        │   ├── POPIA Router (High Risk) → Sprint 3 <-- coverage_debt.md:126
        │   └── JWT Keyring (Medium Risk) → Sprint 2 <-- coverage_debt.md:119
        │
        └── P1 Modules (Core Product)
            ├── Repositories (Medium Risk) → Sprint 5 <-- coverage_debt.md:136
            ├── Services (Medium Risk) → Sprint 4 <-- coverage_debt.md:130
            └── Content Factory → Sprint 4 <-- coverage_debt.md:132
```

**Location ID: 4a**
- **Title:** P0 security module - low risk
- **Description:** Security module at 94% coverage classified as P0 criticality but low risk
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:72

**Location ID: 4b**
- **Title:** P0 auth router - high risk
- **Description:** Auth router at 38.7% coverage, P0 criticality with high risk due to security implications
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:74

**Location ID: 4c**
- **Title:** P0 POPIA router - high risk
- **Description:** POPIA router at 38.7% coverage, P0 criticality due to legal compliance requirements
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:75

**Location ID: 4d**
- **Title:** P0 JWT keyring - medium risk
- **Description:** JWT keyring service at 53.9% coverage, P0 criticality for token security
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:76

**Location ID: 4e**
- **Title:** P1 repositories - medium risk
- **Description:** Repository layer at 41.5% coverage, P1 priority with medium risk
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:81

### AI Guide: Module Risk Classification and Priority Assignment

**Motivation:**
The risk classification system prioritizes coverage improvement efforts based on module criticality and coverage gaps. The P0/P1/P2 priority matrix focuses resources on high-impact areas by combining criticality levels with risk levels.

**Details:**

**Baseline Data**
Baseline data provides coverage percentages per module: security at 94% (low risk), auth/POPIA at 38.7% (high risk), JWT keyring at 53.9% (medium risk), and repositories at 41.5% (medium risk) [4a][4b][4c][4d][4e]. This data informs the risk classification.

**Criticality and Risk Levels**
Criticality levels are P0 (critical security/legal), P1 (core product), and P2 (nice-to-have) based on business impact. Risk levels are high (critical gaps), medium (moderate gaps), and low (minor gaps) based on coverage percentage.

**Classification Matrix and Sprint Assignments**
The classification matrix combines criticality and risk to assign sprint priorities, ensuring focused effort. Sprint assignments are: Sprint 2 (security, auth router, JWT keyring), Sprint 3 (POPIA router), Sprint 4 (services, content factory), and Sprint 5 (repositories).

## Trace ID: 5
**Title:** Quick-Win Test Opportunities and Coverage Impact

**Description:** Identified quick-win test opportunities targeting 2.8% coverage gain through strategic test additions in high-impact, low-effort areas.

**Motivation:**
EduBoost V2 implements a quick-win identification system to close the 2.5% coverage gap to the 60% CI threshold efficiently. The system identifies high-impact, low-effort test opportunities: auth router contract tests (~120 lines, 0.3%), POPIA router contract tests (~150 lines, 0.3%), repository direct tests (~400 lines, 0.9%), and service contract tests (~600 lines, 1.3%). Combined, these quick-wins add ~1,270 lines of coverage (~2.8% overall), exceeding the 2.5% gap. This approach focuses on targeted, achievable wins rather than comprehensive coverage overhaul, enabling rapid progress toward the threshold while building momentum for larger improvements.

**Details:**
- **Execution Flow:** Quick-Win Identification Process with Auth Router Contract Tests (Target: app/api_v2_routers/auth.py, Current: 38.7% coverage, Method: FastAPI TestClient + mocks, Impact: +120 lines (~0.3%)), POPIA Router Contract Tests (Target: app/api_v2_routers/popia.py, Current: 38.7% coverage, Method: TestClient + ConsentService mock, Impact: +150 lines (~0.3%)), Repository Direct Tests (Target: app.repositories, Current: 41.5% coverage, Method: In-memory DB tests, Impact: +400 lines (~0.9%)), Service Contract Tests (Target: app.services (stripe, factory), Current: 53.9% coverage, Method: Targeted unit tests, Impact: +600 lines (~1.3%)) → Total Quick-Win Impact (Combined: ~1,270 lines covered, Overall gain: ~2.8%, Result: Exceeds 2.5% gap to 60%)
- **Concurrency Safety:** Test identification is stateless. Test execution is isolated per test. No distributed locks needed as tests are independent. Multiple quick-wins can be implemented concurrently
- **Covered Objects:** Auth router (auth.py), POPIA router (popia.py), Repository layer (app.repositories), Service layer (app.services), FastAPI TestClient, Mocked services, In-memory DB tests, Coverage impact estimates
- **Timeouts:** Auth router tests: ~5-10min. POPIA router tests: ~5-10min. Repository tests: ~10-20min. Service tests: ~15-30min. Total quick-win implementation: ~35-70min
- **Migration Path:** From gap analysis to quick-win implementation. Migration requires: 1) Identify high-impact, low-effort targets, 2) Estimate coverage impact, 3. Implement tests, 4) Verify coverage gain, 5) Update baseline
- **Error Handling:** Test failures logged. Coverage estimates may vary. Implementation may take longer than estimated. All errors documented in test results
- **Security Considerations:** Auth router tests critical for security. POPIA router tests critical for compliance. Repository tests ensure data access coverage. Service tests ensure business logic coverage

**Trace text diagram:**
```
Coverage Debt Quick-Win Test Opportunities
├── Quick-Win Identification Process
│   ├── Auth Router Contract Tests <-- 5a
│   │   ├── Target: app/api_v2_routers/auth.py <-- auth.py:1
│   │   ├── Current: 38.7% coverage <-- coverage_debt.md:74
│   │   ├── Method: FastAPI TestClient + mocks <-- coverage_debt.md:93
│   │   └── Impact: +120 lines (~0.3%)
│   ├── POPIA Router Contract Tests <-- 5b
│   │   ├── Target: app/api_v2_routers/popia.py <-- popia.py:1
│   │   ├── Current: 38.7% coverage <-- coverage_debt.md:75
│   │   ├── Method: TestClient + ConsentService mock <-- coverage_debt.md:96
│   │   └── Impact: +150 lines (~0.3%)
│   ├── Repository Direct Tests <-- 5c
│   │   ├── Target: app.repositories <-- __init__.py:1
│   │   ├── Current: 41.5% coverage <-- coverage_debt.md:81
│   │   ├── Method: In-memory DB tests <-- coverage_debt.md:99
│   │   └── Impact: +400 lines (~0.9%)
│   └── Service Contract Tests <-- 5d
│       ├── Target: app.services (stripe, factory) <-- __init__.py:1
│       ├── Current: 53.9% coverage <-- coverage_debt.md:78
│       ├── Method: Targeted unit tests <-- coverage_debt.md:102
│       └── Impact: +600 lines (~1.3%)
└── Total Quick-Win Impact <-- 5e
    ├── Combined: ~1,270 lines covered
    ├── Overall gain: ~2.8%
    └── Result: Exceeds 2.5% gap to 60% <-- coverage_debt.md:105
```

**Location ID: 5a**
- **Title:** Quick-win #1: Auth router tests
- **Description:** FastAPI TestClient with mocked services could add ~120 lines (~0.3% overall coverage)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:92

**Location ID: 5b**
- **Title:** Quick-win #2: POPIA router tests
- **Description:** FastAPI TestClient with mocked ConsentService could add ~150 lines (~0.3% overall)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:95

**Location ID: 5c**
- **Title:** Quick-win #3: Repository tests
- **Description:** In-memory DB tests could add ~400 lines (~0.9% overall coverage)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:98

**Location ID: 5d**
- **Title:** Quick-win #4: Service tests
- **Description:** Targeted tests for stripe_service, content_factory could add ~600 lines (~1.3% overall)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:101

**Location ID: 5e**
- **Title:** Total quick-win impact
- **Description:** Combined quick-wins add 2.8% coverage, exceeding the 2.5% gap to reach 60% threshold
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:104

### AI Guide: Quick-Win Test Opportunities and Coverage Impact

**Motivation:**
The quick-win identification system targets high-impact, low-effort test additions to close the coverage gap efficiently. Strategic test additions can exceed the 2.5% gap to reach the 60% threshold by focusing on critical modules with measurable impact.

**Details:**

**Auth and POPIA Router Tests**
Auth router tests use FastAPI TestClient with mocks, covering ~120 lines with ~0.3% impact and critical for security [5a]. POPIA router tests use TestClient with ConsentService mock, covering ~150 lines with ~0.3% impact and critical for compliance [5b].

**Repository and Service Tests**
Repository tests use in-memory DB tests, covering ~400 lines with ~0.9% impact for data access coverage [5c]. Service tests use targeted unit tests, covering ~600 lines with ~1.3% impact for business logic coverage [5d].

**Total Impact**
The total impact is ~1,270 lines covered with ~2.8% overall gain, exceeding the 2.5% gap [5e]. This provides a clear path to reaching the 60% threshold through focused test additions.

## Trace ID: 6
**Title:** Recovery Sprint Plan Execution Roadmap

**Description:** Five-sprint recovery plan progressing from P0 security/auth coverage through P1 core product and repository coverage.

**Motivation:**
EduBoost V2 implements a five-sprint recovery plan to systematically close the coverage gap and reach the 60% CI threshold. The plan progresses from Sprint 1 (unblock measurement - COMPLETE) through Sprint 2 (P0 security/auth), Sprint 3 (P0 POPIA/consent), Sprint 4 (P1 core product), to Sprint 5 (P1 repositories). This phased approach ensures critical security/legal modules are addressed first (Sprint 2-3) before focusing on core product features (Sprint 4-5). Each sprint has specific deliverables (JWT keyring tests, auth router tests, POPIA router tests, etc.) with clear success criteria. The plan provides a structured path to coverage recovery, enabling tracking of progress and resource allocation.

**Details:**
- **Execution Flow:** Sprint Execution Timeline with Sprint 1: Unblock measurement (✓ Add .coveragerc async config, ✓ Run full-suite coverage, ✓ Establish 57.5% baseline), Sprint 2: P0 security/auth ([ ] JWT keyring unit tests, [ ] Token config unit tests, [ ] Security helper unit tests, [ ] Auth router contract tests), Sprint 3: P0 POPIA/consent ([ ] POPIA router contract tests, [ ] Consent service unit tests, [ ] Consent repository unit tests), Sprint 4: P1 core product ([ ] Content factory service tests, [ ] Lesson generation pipeline tests, [ ] Assessment service tests), Sprint 5: P1 repositories ([ ] Direct repository tests (in-memory), [ ] Integration tests (critical paths)) → Target Outcome (Close 2.5% gap to reach 60% threshold)
- **Concurrency Safety:** Sprint execution is sequential (not concurrent). Test implementation is isolated per sprint. No distributed locks needed as sprints are independent. Multiple developers can work on different sprints
- **Covered Objects:** Sprint 1 (measurement unblock), Sprint 2 (P0 security/auth), Sprint 3 (P0 POPIA/consent), Sprint 4 (P1 core product), Sprint 5 (P1 repositories), Test deliverables, Coverage targets
- **Timeouts:** Sprint 1: COMPLETE. Sprint 2: ~1-2 weeks. Sprint 3: ~1-2 weeks. Sprint 4: ~2-3 weeks. Sprint 5: ~1-2 weeks. Total recovery: ~5-9 weeks
- **Migration Path:** From ad-hoc testing to systematic recovery. Migration requires: 1) Define sprint scope, 2) Assign deliverables, 3) Execute sprints sequentially, 4) Track progress, 5) Verify coverage gain
- **Error Handling:** Sprint delays logged. Test failures addressed in sprint. Coverage shortfalls addressed in next sprint. All errors documented in sprint reports
- **Security Considerations:** Sprint 2-3 prioritize security/legal. Auth router tests critical. POPIA router tests critical for compliance. Ensures critical gaps addressed first

**Trace text diagram:**
```
Coverage Debt Recovery Sprint Plan
├── Sprint Execution Timeline
│   ├── Sprint 1: Unblock measurement <-- 6a
│   │   ├── ✓ Add .coveragerc async config <-- coverage_debt.md:113
│   │   ├── ✓ Run full-suite coverage <-- coverage_debt.md:114
│   │   └── ✓ Establish 57.5% baseline <-- coverage_debt.md:115
│   ├── Sprint 2: P0 security/auth <-- 6b
│   │   ├── [ ] JWT keyring unit tests <-- coverage_debt.md:119
│   │   ├── [ ] Token config unit tests <-- coverage_debt.md:120
│   │   ├── [ ] Security helper unit tests <-- coverage_debt.md:121
│   │   └── [ ] Auth router contract tests <-- coverage_debt.md:122
│   ├── Sprint 3: P0 POPIA/consent <-- 6c
│   │   ├── [ ] POPIA router contract tests <-- coverage_debt.md:126
│   │   ├── [ ] Consent service unit tests <-- coverage_debt.md:127
│   │   └── [ ] Consent repository unit tests <-- coverage_debt.md:128
│   ├── Sprint 4: P1 core product <-- 6d
│   │   ├── [ ] Content factory service tests <-- coverage_debt.md:132
│   │   ├── [ ] Lesson generation pipeline tests <-- coverage_debt.md:133
│   │   └── [ ] Assessment service tests <-- coverage_debt.md:134
│   └── Sprint 5: P1 repositories <-- 6e
│       ├── [ ] Direct repository tests (in-memory) <-- coverage_debt.md:138
│       └── [ ] Integration tests (critical paths) <-- coverage_debt.md:139
└── Target Outcome
    └── Close 2.5% gap to reach 60% threshold <-- coverage_debt.md:104
```

**Location ID: 6a**
- **Title:** Sprint 1 completion
- **Description:** Completed: Added .coveragerc, ran full-suite coverage, established 57.5% baseline
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:111

**Location ID: 6b**
- **Title:** Sprint 2: P0 security/auth
- **Description:** Next sprint targeting JWT keyring, token config, security helpers, and auth router tests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:117

**Location ID: 6c**
- **Title:** Sprint 3: P0 POPIA/consent
- **Description:** POPIA router, consent service, and consent repository tests for legal compliance
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:124

**Location ID: 6d**
- **Title:** Sprint 4: P1 core product
- **Description:** Content factory service, lesson generation pipeline, and assessment service tests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:130

**Location ID: 6e**
- **Title:** Sprint 5: P1 repositories
- **Description:** Direct repository tests with in-memory DB and integration tests for critical paths
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:136

### AI Guide: Recovery Sprint Plan Execution Roadmap

**Motivation:**
The recovery sprint plan provides a structured path to systematically close the coverage gap. The five-sprint plan prioritizes critical modules and tracks progress toward the 60% threshold by executing sprints sequentially and verifying coverage gain after each sprint.

**Details:**

**Sprint 1: Unblock Measurement**
Sprint 1 is complete and focused on unblocking measurement by adding .coveragerc async config, running full-suite coverage, and establishing the 57.5% baseline [6a]. This was the foundational sprint that enabled accurate coverage measurement.

**Sprint 2: P0 Security/Auth**
Sprint 2 focuses on P0 security/auth with JWT keyring tests, token config tests, security helper tests, and auth router contract tests [6b]. This addresses critical security gaps.

**Sprint 3: P0 POPIA/Consent**
Sprint 3 focuses on P0 POPIA/consent with POPIA router tests, consent service tests, consent repository tests for legal compliance [6c]. This addresses critical compliance gaps.

**Sprint 4: P1 Core Product**
Sprint 4 focuses on P1 core product with content factory service tests, lesson generation pipeline tests, and assessment service tests [6d]. This addresses core product functionality.

**Sprint 5: P1 Repositories**
Sprint 5 focuses on P1 repositories with direct repository tests (in-memory) and integration tests (critical paths) [6e]. This addresses data access coverage gaps.

## Trace ID: 7
**Title:** Coverage Exemptions and Quality Thresholds

**Description:** Exemption policy for auto-generated code and boilerplate, plus quality threshold contract defining 70% production target.

**Motivation:**
EduBoost V2 implements a coverage exemption policy and quality threshold contract to balance coverage requirements with practical constraints. The exemption policy allows specific categories to be excluded from coverage measurement: auto-generated code (Pydantic schemas tested implicitly through API validation), database migrations (Alembic versions tested through migration execution), dev-only fixtures (guarded by environment), envelope route boilerplate (framework wrapper), and health check endpoints (always public, always exercised). Exemptions require engineering lead approval for governance. The quality threshold contract defines 70% as the minimum coverage target for production readiness, higher than the 60% CI threshold, ensuring production code meets higher quality standards.

**Details:**
- **Execution Flow:** Coverage Exemption Categories with Auto-generated code exemption (Pydantic schemas (implicit validation)), Database migrations exemption (Alembic versions (tested via upgrade)), Exemption governance process (Engineering lead approval required) → Quality Threshold Contracts with Production readiness requirements (70% minimum coverage target)
- **Concurrency Safety:** Exemption policy is stateless. Approval process is manual. No distributed locks needed as operations are read-only. Multiple exemption requests can be processed concurrently
- **Covered Objects:** Exemption categories (auto-generated, migrations, dev-only, boilerplate, health checks), Exemption governance process, Quality threshold contract, Production readiness requirements, 70% coverage target
- **Timeouts:** Exemption evaluation: ~1-5min. Approval process: ~1-2 days. Threshold contract review: ~1-5min
- **Migration Path:** From no exemptions to governed policy. Migration requires: 1) Define exemption categories, 2) Document rationale, 3) Implement approval process, 4) Define quality thresholds, 5) Communicate to team
- **Error Handling:** Invalid exemptions rejected. Missing approval logged. Threshold violations fail production readiness. All errors documented in exemption log
- **Security Considerations:** Exemptions require approval for governance. Auto-generated code exempted (implicitly tested). Migrations exempted (tested via execution). Production threshold higher than CI (70% vs 60%)

**Trace text diagram:**
```
Coverage Quality & Exemption Policy System
├── Coverage Exemption Categories <-- coverage_debt.md:143
│   ├── Auto-generated code exemption <-- 7a
│   │   └── Pydantic schemas (implicit validation)
│   ├── Database migrations exemption <-- 7b
│   │   └── Alembic versions (tested via upgrade)
│   └── Exemption governance process <-- 7c
│       └── Engineering lead approval required
└── Quality Threshold Contracts <-- coverage_quality_threshold_contract.md:1
    └── Production readiness requirements <-- 7d
        └── 70% minimum coverage target
```

**Location ID: 7a**
- **Title:** Exemption: Auto-generated schemas
- **Description:** Pydantic schemas exempted as they're tested implicitly through API request validation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:150

**Location ID: 7b**
- **Title:** Exemption: Database migrations
- **Description:** Alembic migrations exempted as they're tested through migration execution, not unit tests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:151

**Location ID: 7c**
- **Title:** Exemption approval process
- **Description:** Governance control requiring engineering lead approval for any new coverage exemptions
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/engineering/coverage_debt.md:156

**Location ID: 7d**
- **Title:** Production coverage target
- **Description:** Long-term quality contract requiring 70% coverage for production readiness
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/testing/coverage_quality_threshold_contract.md:20

### AI Guide: Coverage Exemptions and Quality Thresholds

**Motivation:**
The coverage exemption policy and quality threshold contract balance coverage requirements with practical constraints. Exemptions are governed through an approval process, and production readiness is defined with a higher threshold than CI to ensure quality.

**Details:**

**Exemption Categories and Rationale**
Exemption categories include auto-generated code (Pydantic schemas), database migrations (Alembic), dev-only fixtures, boilerplate code, and health check endpoints [7a][7b]. Exemption rationale includes implicit testing (schemas), alternative testing (migrations), environment guards (dev-only), framework wrappers (boilerplate), and always exercised (health checks).

**Governance Process**
The governance process requires engineering lead approval, documented rationale, and a review process to prevent abuse [7c]. This ensures that exemptions are only granted for valid reasons and are properly documented.

**Quality Threshold**
The quality threshold sets a 70% production target, which is higher than CI (60%) as a long-term contract for production readiness [7d]. This balance provides exemptions for practical constraints while maintaining a higher production threshold for quality through governance and clear documentation.
