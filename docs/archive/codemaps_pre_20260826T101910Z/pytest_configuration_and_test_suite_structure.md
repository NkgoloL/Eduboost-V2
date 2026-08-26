# Pytest Configuration and Test Suite Structure

Maps pytest configuration from pytest.ini through test discovery, fixture hierarchy, coverage reporting, and CI execution. Key configuration at [1a], marker definitions at [2b], database fixtures at [3a-3d], coverage thresholds at [4d], and CI test execution at [5a-5b].

## Trace ID: 1
**Title:** Pytest initialization and core configuration

**Description:** Root pytest.ini settings that control test execution behavior, async support, and test discovery paths

**Motivation:**
EduBoost V2 uses pytest as its primary test framework due to its powerful fixture system, async test support, and extensive plugin ecosystem. The pytest.ini configuration centralizes test discovery rules, async mode settings, and marker definitions to ensure consistent test execution across development environments and CI pipelines. This configuration enables automatic async test detection without requiring decorators, enforces marker registration to prevent typos, and optimizes test discovery by excluding irrelevant directories. The configuration balances developer experience (automatic discovery, sensible defaults) with CI requirements (strict markers, coverage integration).

**Details:**
- **Execution Flow:** pytest reads pytest.ini from project root → Parses [pytest] section → Enables asyncio_mode=auto for async tests → Sets test discovery paths (tests/, test_*.py, Test*, test_*) → Applies addopts (--strict-markers, --tb=short, --cov=app) → Registers custom markers from [markers] section → Applies warning filters from [filterwarnings] section → Discovers and executes tests
- **Concurrency Safety:** pytest test collection is sequential. Test execution can be parallelized with pytest-xdist. Async tests run in event loop managed by pytest-asyncio. No distributed locks needed as tests are isolated. Fixture setup/teardown respects scope (session, function)
- **Covered Objects:** pytest.ini configuration file, Test discovery patterns (testpaths, python_files, python_classes, python_functions), Async mode settings (asyncio_mode), Marker definitions ([markers] section), Warning filters ([filterwarnings] section), Coverage settings (--cov=app)
- **Timeouts:** pytest.ini parsing: <1ms. Test collection: ~100-500ms depending on test count. Async test setup: ~10-50ms per test. Overall test execution varies by test category
- **Migration Path:** From unittest or nose to pytest. Migration requires: 1) Create pytest.ini with configuration, 2) Rename test files to test_*.py pattern, 3) Convert test methods to pytest format, 4) Add pytest-asyncio for async tests, 5) Migrate fixtures to pytest fixtures, 6) Update CI to use pytest
- **Error Handling:** Invalid pytest.ini syntax causes pytest to fail with clear error message. Missing pytest-asyncio causes async tests to fail. Unregistered markers with --strict-markers cause warnings (or errors if configured). Invalid test discovery patterns result in no tests collected
- **Security Considerations:** pytest.ini should not contain secrets. Test discovery patterns should not accidentally collect sensitive files. Coverage reports should not be committed to git (via .gitignore). Marker names should be descriptive and not expose internal implementation details

**Trace text diagram:**
```
pytest.ini Configuration File
├── [pytest] section <-- pytest.ini:9
│   ├── asyncio_mode = auto <-- 1a
│   ├── testpaths = tests <-- 1b
│   ├── norecursedirs = ... tests/legacy <-- 1c
│   ├── python_files = test_*.py <-- 1d
│   └── python_classes = Test* <-- pytest.ini:14
│       └── python_functions = test_* <-- pytest.ini:15
├── addopts section <-- pytest.ini:18
│   ├── --strict-markers <-- 1e
│   ├── --tb=short <-- pytest.ini:20
│   └── --cov=app (coverage settings) <-- pytest.ini:21
├── markers section <-- pytest.ini:28
│   └── (marker definitions)
└── filterwarnings section <-- pytest.ini:38
    └── (warning filters)
```

**Location ID: 1a**
- **Title:** Async test auto-detection
- **Description:** Enables automatic asyncio mode for async test functions without explicit decorator
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:10

**Location ID: 1b**
- **Title:** Test discovery root
- **Description:** Defines tests/ as the root directory for test discovery
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:11

**Location ID: 1c**
- **Title:** Excluded directories
- **Description:** Excludes tests/legacy and common build/cache directories from test discovery
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:12

**Location ID: 1d**
- **Title:** Test file pattern
- **Description:** Discovers only files matching test_*.py naming convention
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:13

**Location ID: 1e**
- **Title:** Marker validation
- **Description:** Enforces that all markers used in tests are registered in pytest.ini
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:19

### AI Guide: Pytest Initialization and Core Configuration

**Motivation:**
The fundamental pytest configuration controls how tests are discovered, executed, and reported. The `pytest.ini` file is the central configuration file that pytest reads automatically when run from the project root, ensuring consistent test behavior across the project.

**Details:**

**Async Test Support**
Async test support uses `asyncio_mode = auto` to enable pytest-asyncio to automatically detect and run async test functions without the need to decorate with `@pytest.mark.asyncio` [1a]. This is essential for testing FastAPI endpoints and async database operations and should be kept enabled for consistency across the test suite.

**Test Discovery and Directory Exclusion**
Test discovery uses `testpaths = tests` to restrict discovery to the tests/ directory, `python_files = test_*.py` to ensure only files matching this pattern are collected, and `python_classes = Test*` and `python_functions = test_*` to define naming conventions [1b-1d]. Directory exclusion uses `norecursedirs` to exclude build artifacts, virtual environments, and legacy test directories to prevent pytest from wasting time scanning irrelevant directories [1c].

**Marker Validation**
Marker validation uses `--strict-markers` to ensure all markers are registered in pytest.ini, preventing typos in marker names and enforcing consistency across the team [1e]. Always register new markers in the `[markers]` section before use. Best practices include keeping pytest.ini in the project root for automatic discovery, using descriptive test names that follow the `test_*` pattern, registering all markers before using them in tests, periodically reviewing and updating `norecursedirs` as project structure evolves, and using `pytest --collect-only` to verify test discovery without running tests.

## Trace ID: 2
**Title:** Test categorization with custom markers

**Description:** Marker definitions in pytest.ini and their application across test suites for selective test execution

**Motivation:**
EduBoost V2 implements a test categorization system using pytest markers to enable selective test execution based on test characteristics such as speed, dependencies, and purpose. This system allows developers to run fast unit tests during development for rapid feedback, run integration tests to verify component interactions, run smoke tests in CI for critical path validation, and conditionally skip expensive tests like LLM API calls. The marker system with --strict-markers enforcement prevents typos and ensures consistency across the team. Module-level marker application reduces boilerplate by automatically applying markers to entire directories or files.

**Details:**
- **Execution Flow:** pytest reads [markers] section from pytest.ini → Registers markers (unit, integration, e2e, llm, smoke) → During test collection, applies module-level markers from conftest.py → During test execution, filters tests based on -m marker expression → Executes only matching tests → Skips tests not matching expression
- **Concurrency Safety:** Marker registration is read-only and happens at pytest startup. Test filtering is deterministic based on marker expressions. No distributed locks needed as markers are static metadata. Test execution respects marker-based filtering regardless of parallelization
- **Covered Objects:** pytest.ini [markers] section, Module-level pytestmark variables, Function-level @pytest.mark decorators, Class-level @pytest.mark decorators, Marker expressions (-m flag), Test selection logic
- **Timeouts:** Marker registration: <1ms. Test collection with marker filtering: ~100-500ms. Marker expression evaluation: <1ms per test. Overall impact on test execution is minimal
- **Migration Path:** From unmarked tests to categorized tests. Migration requires: 1) Define markers in pytest.ini, 2) Add module-level markers to conftest.py files, 3) Add function-level markers to individual tests, 4) Update CI to use marker-based filtering, 5) Gradually increase test coverage with appropriate markers
- **Error Handling:** Unregistered markers with --strict-markers cause warnings. Invalid marker expressions cause pytest to fail with error. Missing markers on tests that should have them results in tests not being filtered correctly. Typos in marker names caught by --strict-markers
- **Security Considerations:** Marker names should not expose sensitive implementation details. Marker-based filtering should not be used to skip security-critical tests. LLM tests should be conditionally skipped in CI to prevent API key exposure. Marker descriptions in pytest.ini should be accurate and helpful

**Trace text diagram:**
```
Pytest Test Categorization System
├── pytest.ini configuration file <-- pytest.ini:28
│   ├── [markers] section start <-- 2a
│   ├── unit marker definition <-- 2b
│   ├── integration marker definition <-- 2c
│   ├── e2e marker definition <-- 2d
│   └── llm marker definition <-- 2e
│
└── Test suite marker application
    ├── tests/integration/conftest.py <-- conftest.py:1
    │   └── pytestmark = integration <-- 2f
    │       └── (applies to all tests in directory)
    │
    └── tests/smoke/test_*.py <-- test_content_factory_admin_api_smoke.py:1
        └── pytestmark = smoke <-- 2g
            └── (applies to all tests in module)
```

**Location ID: 2a**
- **Title:** Marker registry start
- **Description:** Beginning of custom marker definitions for test categorization
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:28

**Location ID: 2b**
- **Title:** Unit test marker
- **Description:** Marks fast, isolated tests with no external I/O dependencies
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:29

**Location ID: 2c**
- **Title:** Integration test marker
- **Description:** Marks tests requiring live database or Redis connections
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:30

**Location ID: 2d**
- **Title:** E2E test marker
- **Description:** Marks Playwright-based end-to-end tests requiring full stack
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:31

**Location ID: 2e**
- **Title:** LLM test marker
- **Description:** Marks tests making real LLM API calls, conditionally skipped in CI
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:33

**Location ID: 2f**
- **Title:** Module-level marker application
- **Description:** Applies integration marker to all tests in integration/ directory
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/conftest.py:5

**Location ID: 2g**
- **Title:** Smoke test marker application
- **Description:** Applies smoke marker to critical-path smoke tests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/smoke/test_content_factory_admin_api_smoke.py:8

### AI Guide: Test Categorization with Custom Markers

**Motivation:**
Custom markers enable selective test execution based on test characteristics such as speed, dependencies, or purpose. This system allows running specific test subsets during development, CI pipelines, or debugging to optimize test execution efficiency.

**Details:**

**Unit and Integration Tests**
Unit tests are fast, isolated tests with no external I/O dependencies that run frequently during development with `pytest -m unit`, should complete in milliseconds to seconds, use mocks for external dependencies, and are ideal for TDD and rapid feedback loops [2b]. Integration tests require live database or Redis connections, test interactions between components, are slower than unit tests but faster than E2E tests, run with `pytest -m integration` or `pytest tests/integration`, and use a module-level marker that automatically applies to all tests in integration/ [2c][2f].

**E2E and LLM Tests**
E2E tests are Playwright-based browser tests requiring full stack that test complete user flows from UI to database, are the slowest test category and run sparingly, require a running application stack, and execute with `pytest -m e2e` or `npx playwright test` [2d]. LLM tests make real LLM API calls, are conditionally skipped in CI unless `ALLOW_LLM_TESTS` is set, are expensive and potentially flaky due to external API dependencies, are used for validating LLM integration behavior, and run with `pytest -m llm -k "not ci"` locally [2e].

**Smoke Tests**
Smoke tests are critical-path tests that verify core functionality and should pass before any deployment [2g]. This categorization enables selective test execution based on test characteristics and dependencies. Best practices include always registering markers in pytest.ini before use, using module-level markers for directory-wide categorization, keeping unit tests fast and isolated, running smoke tests first in CI for fast feedback, documenting marker purpose in pytest.ini descriptions, using marker combinations for complex selection logic, and considering test speed when assigning markers. Common patterns include development with `pytest -m unit` for rapid iteration, pre-commit with `pytest -m "unit and not slow"` for quick checks, CI fast lane with `pytest -m smoke` for critical path validation, CI full suite with `pytest tests/` with appropriate markers, and debugging with `pytest -m "integration and test_name"` for targeted testing.
```

**Selective Test Execution:**

```bash
# Run only unit tests
pytest -m unit

# Run integration and e2e tests
pytest -m "integration or e2e"

# Skip slow tests
pytest -m "not slow"

# Run smoke tests only
pytest -m smoke
```

## Trace ID: 3
**Title:** Database fixture hierarchy for test isolation

**Description:** Session and function-scoped fixtures in conftest.py files that manage test database lifecycle and provide clean sessions

**Motivation:**
EduBoost V2 uses a hierarchical fixture system to manage database test isolation and lifecycle. Session-scoped fixtures (test_db_setup) run once per test session to create the database schema, optimizing performance by avoiding repeated schema creation. Function-scoped fixtures (db_session) provide fresh database sessions for each test, ensuring test isolation by rolling back transactions after each test. This approach balances performance (schema created once) with isolation (each test gets clean state). The fixture hierarchy also includes Redis patching for integration tests, using fakeredis to avoid external dependencies. This system enables fast, reliable database testing without requiring a live database for unit tests.

**Details:**
- **Execution Flow:** pytest starts test session → test_db_setup fixture runs (session scope) → Drops all tables → Creates fresh schema → Yields session-wide DB schema → For each test: db_session fixture runs (function scope) → Creates async database session → Yields session to test → Test executes → Session rolls back or closes → After all tests: test_db_setup cleanup runs
- **Concurrency Safety:** Session-scoped fixtures run once before parallel test execution. Function-scoped fixtures are independent per test. Database transactions provide isolation between tests. Redis patching uses monkeypatch for thread-safe replacement. No distributed locks needed as tests are isolated. With pytest-xdist, each worker gets its own database
- **Covered Objects:** test_db_setup fixture (session scope), db_session fixture (function scope), integration_db fixture (integration scope), Redis patching fixture (autouse), Database schema, Async database sessions, Transaction management, fakeredis instances
- **Timeouts:** Session setup (drop/create tables): ~1-5s. Function-scoped session creation: ~10-50ms. Test execution: varies by test. Session cleanup: ~10-50ms. Overall test session: depends on test count
- **Migration Path:** From ad-hoc database setup to fixture-based system. Migration requires: 1) Create conftest.py with session-scoped fixture, 2) Add function-scoped session fixture, 3) Update tests to use fixtures, 4) Add Redis patching for integration tests, 5) Remove ad-hoc setup code from tests
- **Error Handling:** Database connection failures cause fixture to fail and tests to skip. Schema creation failures fail the test session. Session cleanup failures logged but don't block test completion. Redis patching failures fail affected tests. All errors logged with clear messages
- **Security Considerations:** Test database should be separate from production database. Test credentials should not be production credentials. Database schema in tests should match production schema. Redis patching should not affect production Redis. Test data should not include sensitive information

**Trace text diagram:**
```
Pytest Test Database Fixture Hierarchy
├── tests/conftest.py (root-level fixtures)
│   ├── @pytest_asyncio.fixture(scope="session") <-- 3a
│   │   async def test_db_setup(): <-- conftest.py:33
│   │   ├── await drop_all_tables() <-- 3b
│   │   ├── await create_all_tables() <-- 3c
│   │   └── yield (session-wide DB schema) <-- conftest.py:52
│   │
│   └── @pytest_asyncio.fixture <-- 3d
│       async def db_session(test_db_setup): <-- conftest.py:58
│       └── async with AsyncSessionFactory() <-- conftest.py:60
│           └── yield session (per-test isolation) <-- conftest.py:61
│
└── tests/integration/conftest.py (integration)
    ├── async def integration_db(test_db_setup) <-- 3e
    │   └── yield (depends on root fixture) <-- conftest.py:14
    │
    └── @pytest.fixture(autouse=True) <-- conftest.py:89
        def patch_redis(monkeypatch, fake_redis): <-- conftest.py:90
        └── monkeypatch.setattr(...) <-- 3f
```

**Location ID: 3a**
- **Title:** Session-scoped DB setup
- **Description:** Creates fixture that runs once per test session for database schema setup
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/conftest.py:32

**Location ID: 3b**
- **Title:** Drop existing tables
- **Description:** Clears all database tables before test session starts
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/conftest.py:44

**Location ID: 3c**
- **Title:** Create fresh schema
- **Description:** Creates clean database schema for test session
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/conftest.py:45

**Location ID: 3d**
- **Title:** Function-scoped session
- **Description:** Provides fresh async database session for each individual test
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/conftest.py:57

**Location ID: 3e**
- **Title:** Integration DB fixture
- **Description:** Integration-specific fixture that depends on root test_db_setup
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/conftest.py:12

**Location ID: 3f**
- **Title:** Redis patching
- **Description:** Patches Redis connections to use in-memory fake for integration tests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/conftest.py:95

### AI Guide: Database Fixture Hierarchy for Test Isolation

**Motivation:**
The fixture hierarchy provides clean database state for each test while optimizing performance through session-level schema setup. This pattern ensures test isolation without the overhead of recreating the database schema for every test.

**Details:**

**Session-Scoped Schema Setup**
Session-scoped schema setup uses `test_db_setup` that runs once per pytest session, drops all existing tables to ensure clean state, creates fresh schema from Alembic migrations, yields control to all tests in the session, and cleanup happens after all tests complete [3a-3c]. This is a performance optimization since schema creation is expensive.

**Function-Scoped Session and Integration Fixtures**
Function-scoped session uses `db_session` to provide a fresh database session for each test, wraps each test in a transaction that rolls back on completion, ensures tests don't leak data to each other, depends on `test_db_setup` (fixture dependency chain), is AsyncSession compatible with SQLAlchemy async operations, and is critical for test isolation [3d]. Integration-specific fixtures use `integration_db` to extend root fixture for integration tests and `patch_redis` with autouse=True to automatically patch Redis, replacing real Redis with in-memory fake for speed and isolation, patching multiple modules that import Redis, and ensuring integration tests don't require external Redis [3e-3f]. Best practices include always using `db_session` fixture for database access in tests, never committing transactions in tests (rely on rollback), using session-scoped fixtures for expensive setup (schema), using function-scoped fixtures for test isolation (sessions), leveraging autouse for cross-cutting concerns (Redis patching), keeping fixture dependencies minimal and clear, and testing fixture behavior with simple smoke tests. Common issues include tests sharing data (ensure db_session is function-scoped), slow test runs (check if schema is being recreated per test), Redis connection errors (verify patching is applied in conftest), async test failures (use pytest-asyncio fixtures for async tests), and fixture not found (check fixture scope and conftest.py location). Performance considerations include session-scoped fixtures running once per test session, function-scoped fixtures running per test, balancing between isolation and performance, database schema creation being expensive (session-scoped), and session creation being cheap (function-scoped for isolation).

**Transaction Rollback Pattern:**

- Each test runs in its own transaction
- Transaction rolls back after test completes
- No manual cleanup required
- Tests remain isolated regardless of what they do
- Performance: rollback is faster than truncate/delete

**Redis Patching Strategy (3f):**

- Uses `fakeredis` library for in-memory Redis
- Patches at import time via monkeypatch
- Covers all modules that import Redis
- Autouse=True applies to all integration tests automatically
- No test code changes required
- Faster and more reliable than external Redis

## Trace ID: 4
**Title:** Coverage measurement and reporting configuration

**Description:** Coverage settings in pytest.ini that control code coverage collection, reporting formats, and quality gates

**Motivation:**
EduBoost V2 uses pytest-cov to measure code coverage and enforce quality gates. Coverage measurement ensures that code changes are adequately tested, preventing regressions and maintaining code quality. The configuration enables multiple report formats (terminal, HTML, XML) for different use cases: terminal for immediate feedback during development, HTML for detailed interactive browsing, and XML for CI integration with tools like Codecov. The coverage threshold (--cov-fail-under=80) enforces a minimum coverage level, failing the test run if coverage falls below the threshold. This automated quality gate prevents code with insufficient test coverage from being merged.

**Details:**
- **Execution Flow:** pytest starts with --cov=app addopt → pytest-cov plugin activates → Instruments app/ package for coverage collection → Tests execute → Coverage data collected for each line → After tests: generates terminal report with missing lines → Generates HTML report in coverage_html/ → Generates XML report for CI → Validates coverage against threshold (80%) → Fails test run if below threshold
- **Concurrency Safety:** Coverage collection is thread-safe with pytest-xdist. Each worker collects coverage independently. Coverage data merged at end of test run. No distributed locks needed. Coverage instrumentation has minimal performance impact (~10-20% overhead)
- **Covered Objects:** pytest.ini addopts (--cov=app, --cov-report options), pytest-cov plugin, Coverage data structures, Terminal report, HTML report (coverage_html/), XML report (coverage.xml), Coverage threshold (80%), .gitignore (coverage_html/)
- **Timeouts:** Coverage instrumentation: ~10-50ms overhead per test. Report generation: ~100-500ms. Total coverage overhead: ~10-20% of test execution time
- **Migration Path:** From no coverage to coverage measurement. Migration requires: 1) Install pytest-cov, 2) Add --cov=app to pytest.ini addopts, 3) Configure report formats, 4) Set initial low threshold, 5) Gradually increase threshold as coverage improves, 6) Add coverage_html/ to .gitignore
- **Error Handling:** Coverage instrumentation failures logged but don't block tests. Report generation failures logged. Threshold failures fail test run with clear message. Invalid coverage configuration causes pytest to fail with error
- **Security Considerations:** Coverage reports should not be committed to git (HTML reports in .gitignore). Coverage data should not include sensitive information from tests. Coverage thresholds should be realistic and achievable. Coverage reports should not expose internal implementation details publicly

**Trace text diagram:**
```
Pytest Configuration & Execution
├── pytest.ini (root configuration) <-- pytest.ini:1
│   ├── [pytest] section <-- pytest.ini:9
│   │   ├── addopts = coverage settings <-- pytest.ini:18
│   │   │   ├── --cov=app <-- 4a
│   │   │   ├── --cov-report=term-missing <-- 4b
│   │   │   ├── --cov-report=html:coverage_html <-- 4c
│   │   │   └── --cov-fail-under=80 <-- 4d
│   │   └── (other pytest settings)
│   └── pytest reads config on startup
│       └── pytest-cov plugin activates
│           ├── Collects coverage during test run
│           ├── Generates terminal report
│           ├── Generates HTML in coverage_html/
│           └── Validates 80% threshold
└── .gitignore (version control) <-- .gitignore:1
    └── coverage_html/ <-- 4e
```

**Location ID: 4a**
- **Title:** Coverage target
- **Description:** Measures code coverage for the app/ package
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:21

**Location ID: 4b**
- **Title:** Terminal coverage report
- **Description:** Displays coverage report in terminal with missing line numbers
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:22

**Location ID: 4c**
- **Title:** HTML coverage report
- **Description:** Generates browsable HTML coverage report in coverage_html/ directory
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:23

**Location ID: 4d**
- **Title:** Coverage threshold
- **Description:** Fails test run if coverage falls below 80% threshold
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:25

**Location ID: 4e**
- **Title:** Exclude coverage artifacts
- **Description:** Prevents coverage HTML reports from being committed to git
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.gitignore:11

### AI Guide: Coverage Measurement and Reporting Configuration

**Motivation:**
Coverage configuration ensures code quality by measuring how much of the codebase is exercised by tests. The pytest-cov plugin integrates coverage collection with test execution, providing multiple report formats and quality gates to maintain code quality standards.

**Details:**

**Coverage Target and Reports**
The coverage target uses `--cov=app` to measure coverage for the app/ package, excludes test code from coverage measurements, focuses on production code quality, can specify multiple packages, and can use `--cov=` with no value to cover all Python files [4a]. The terminal report uses `--cov-report=term-missing` to show coverage in terminal, highlights line numbers not covered by tests, provides immediate feedback during development, and is useful for identifying gaps in test coverage [4b].

**HTML and XML Reports**
The HTML report uses `--cov-report=html:coverage_html` to generate browsable HTML with interactive report with source code highlighting, color-coded coverage (green=covered, red=uncovered), click-to-navigate through uncovered lines, and is excellent for detailed coverage analysis [4c]. The XML report uses `--cov-report=xml:coverage.xml` to generate machine-readable report used by CI tools (Codecov, Coveralls), enables coverage tracking over time, and is required for coverage badges and dashboards.

**Coverage Threshold**
The coverage threshold uses `--cov-fail-under=80` to fail test run if coverage < 80%, enforcing quality standards and preventing coverage regression [4d]. Best practices include setting realistic coverage thresholds based on project maturity, using HTML reports for detailed coverage analysis, reviewing term-missing output for quick gap identification, keeping coverage reports out of version control, using coverage in CI for quality gates, tracking coverage trends over time, excluding truly untestable code with pragma comments, and focusing on critical path coverage over blanket percentage. Common issues include coverage below threshold (add tests for uncovered lines or adjust threshold), missing coverage data (ensure pytest-cov is installed and configured), slow coverage collection (use `--no-cov` for speed during development), false negatives (check that test files are excluded from coverage), and HTML report not generating (verify directory permissions and disk space). Integration with CI includes coverage running automatically in CI/CD workflow, XML report uploaded to Codecov for tracking, threshold enforced via environment variable, coverage badges displaying status in README, and historical data showing coverage trends. Git exclusion uses `coverage_html/` in .gitignore to prevent commit of reports since HTML reports are generated artifacts not source code, reduces repository size and noise, and is regenerated on each test run [4e].

# Generate coverage without running tests (if .coverage exists)
coverage report

# Generate HTML report only
coverage html

# Combine coverage from multiple test runs
coverage combine
```

**Coverage Report Formats:**

- **Terminal:** Quick feedback during development
- **HTML:** Detailed analysis and exploration
- **XML:** CI integration and tracking
- **JSON:** Programmatic analysis

**Coverage Threshold Strategy:**

- Local development: 80% (pytest.ini)
- CI pipelines: 60% (ci-cd.yml) - more lenient for PRs
- Production releases: May require higher threshold
- New code: Aim for 100% coverage
- Legacy code: Accept lower coverage with documentation

**Excluding Code from Coverage:**

```python
# Exclude specific lines
if __name__ == "__main__":  # pragma: no cover
    main()

# Exclude entire blocks
def debug_function():  # pragma: no cover
    print("Debugging code")
```

## Trace ID: 5
**Title:** CI workflow test execution strategies

**Description:** GitHub Actions workflows that run different test suites with selective coverage reporting and environment setup

**Motivation:**
EduBoost V2 uses GitHub Actions CI workflows to automate test execution with different strategies for different scenarios. The ci-core workflow runs unit and integration tests without coverage for fast feedback during development, enabling quick iteration. The ci-cd workflow runs the full test suite with coverage measurement for comprehensive validation before deployment. This separation balances speed (fast feedback on core tests) with thoroughness (comprehensive validation with coverage). The workflows also integrate with Codecov for coverage tracking over time, providing visibility into code quality trends. Environment-specific coverage thresholds (60% in CI vs 80% locally) accommodate different testing environments.

**Details:**
- **Execution Flow:** GitHub Actions triggers workflow → Sets up Python environment → Installs dependencies → Runs unit tests with --no-cov (ci-core) → Runs integration tests with --no-cov (ci-core) → Sets COVERAGE_THRESHOLD environment variable (ci-cd) → Runs full test suite with coverage (ci-cd) → Uploads coverage.xml to Codecov (ci-cd) → Reports test results and coverage
- **Concurrency Safety:** CI workflows run in isolated GitHub Actions runners. Test execution within workflow can be parallelized with pytest-xdist. Coverage collection is thread-safe. No distributed locks needed as CI runs are isolated. Multiple workflows can run concurrently on different branches
- **Covered Objects:** GitHub Actions workflows (ci-core.yml, ci-cd.yml), Environment variables (COVERAGE_THRESHOLD), Test execution commands (pytest with/without coverage), Codecov integration, Coverage reports, Test results
- **Timeouts:** CI workflow setup: ~1-2min. Unit tests: ~1-5min. Integration tests: ~2-10min. Full test suite with coverage: ~5-20min. Codecov upload: ~30s. Total CI run: ~5-30min depending on test suite
- **Migration Path:** From manual testing to CI automation. Migration requires: 1) Create GitHub Actions workflow files, 2) Configure test execution commands, 3) Add Codecov integration, 4) Set up environment variables, 5) Configure branch protection rules, 6) Gradually increase test coverage
- **Error Handling:** Test failures fail the workflow with clear error messages. Coverage threshold failures fail the workflow. Dependency installation failures fail the workflow. Codecov upload failures logged but don't block workflow. All errors reported in GitHub Actions UI
- **Security Considerations:** CI secrets should be stored in GitHub Secrets. Coverage reports should not include sensitive information. Codecov integration should use secure tokens. Test environment should match production configuration. CI logs should not expose secrets

**Trace text diagram:**
```
GitHub Actions CI Workflows
├── ci-core.yml workflow <-- ci-core.yml:1
│   ├── Unit tests job <-- ci-core.yml:86
│   │   └── pytest tests/unit --no-cov <-- 5a
│   └── Integration tests job <-- ci-core.yml:89
│       └── pytest tests/integration --no-cov <-- 5b
└── ci-cd.yml workflow <-- ci-cd.yml:1
    ├── Environment variables <-- ci-cd.yml:11
    │   └── COVERAGE_THRESHOLD: "60" <-- 5c
    ├── Test execution job <-- ci-cd.yml:150
    │   └── pytest tests/ with coverage <-- 5d
    └── Coverage upload step <-- ci-cd.yml:159
        └── codecov/codecov-action@v4 <-- 5e
```

**Location ID: 5a**
- **Title:** Unit tests without coverage
- **Description:** Runs unit tests in ci-core workflow with coverage disabled for speed
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-core.yml:87

**Location ID: 5b**
- **Title:** Integration tests without coverage
- **Description:** Runs integration tests separately with coverage disabled
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-core.yml:90

**Location ID: 5c**
- **Title:** CI coverage threshold
- **Description:** Sets lower 60% coverage threshold for CI/CD workflow
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:13

**Location ID: 5d**
- **Title:** Full test suite with coverage
- **Description:** Runs complete test suite with coverage measurement in ci-cd workflow
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:153

**Location ID: 5e**
- **Title:** Upload to Codecov
- **Description:** Uploads coverage.xml to Codecov for tracking over time
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:160

### AI Guide: CI Workflow Test Execution Strategies

**Motivation:**
CI workflows implement different test execution strategies for various purposes: fast feedback in core CI, comprehensive coverage in CD pipelines, and selective testing based on workflow goals to optimize CI pipeline efficiency and effectiveness.

**Details:**

**ci-core.yml Workflow**
The ci-core.yml workflow provides fast feedback on every push/PR with unit tests running `pytest tests/unit --no-cov` without coverage for speed, focusing on fast isolated tests for quick validation of code changes and catching obvious bugs early [5a]. Integration tests run `pytest tests/integration --no-cov` without coverage for speed, test component interactions, require database but not full stack, and are slower than unit tests but still relatively fast [5b]. The strategy uses separate jobs for parallel execution with coverage disabled to reduce CI time.

**ci-cd.yml Workflow**
The ci-cd.yml workflow provides comprehensive validation before deployment with environment variables including `COVERAGE_THRESHOLD: "60"` which is lower than local 80% for more lenient PRs to avoid blocking contributions and can be tightened for main branch protection [5c]. The full test suite runs `pytest tests/ --cov=app` to run all tests (unit, integration, smoke), includes coverage measurement, is slower but comprehensive, and only runs on merge to main or deployment [5d]. Coverage upload uses `codecov/codecov-action@v4` to upload coverage.xml to Codecov, tracks coverage over time, and enables coverage badges and trends [5e]. The execution strategy comparison shows ci-core.yml triggers on every push/PR with unit + integration test scope, disabled coverage for speed, and fast (minutes) execution, while ci-cd.yml triggers on merge/deployment with full test suite, enabled coverage, and slower (10+ minutes) execution.
| Purpose | Quick feedback | Comprehensive validation |
| Parallel Jobs | Yes (unit + integration) | Single job |

**CI Workflow Best Practices:**

1. **Fast Lane Strategy:**
   - Run quick tests first in ci-core
   - Provide immediate feedback to developers
   - Block obvious bugs before comprehensive tests
   - Use `--no-cov` for speed in feedback loops

2. **Comprehensive Strategy:**
   - Run full suite in ci-cd before deployment
   - Include coverage for quality gates
   - Upload coverage for tracking
   - Only run on critical branches (main, release)

3. **Parallel Execution:**
   - Split test suites into separate jobs
   - Run unit and integration tests in parallel
   - Reduces total CI time
   - Matrix strategy for multiple Python versions

4. **Coverage Thresholds:**
   - Local: 80% (strict, enforces quality)
   - CI PR: 60% (lenient, encourages contributions)
   - Production: May require higher threshold
   - Adjust based on project maturity

**Workflow Configuration Examples:**

```yaml
# ci-core.yml - Fast feedback
- name: Unit tests
  run: pytest tests/unit -q --no-cov

- name: Integration tests
  run: pytest tests/integration -q --no-cov

# ci-cd.yml - Comprehensive
- name: Test with coverage
  run: |
    pytest tests/ \
      --cov=app \
      --cov-report=xml \
      --cov-report=term-missing \
      --cov-fail-under=${{ env.COVERAGE_THRESHOLD }}

- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    file: coverage.xml
```

**Selective Test Execution in CI:**

```bash
# Run only smoke tests for quick validation
pytest -m smoke

# Run specific test suite
pytest tests/unit -k "test_user"

# Skip slow tests in CI
pytest -m "not slow"

# Run tests for specific module
pytest tests/unit/modules/auth/
```

**Optimizing CI Performance:**

- Use `--no-cov` for fast feedback workflows
- Split test suites into parallel jobs
- Cache dependencies between runs
- Use pytest-xdist for parallel test execution
- Run only changed tests with pytest-dotenv
- Exclude slow tests from PR workflows

**Coverage Integration:**

- Coverage runs in ci-cd, not ci-core (speed)
- XML report uploaded to Codecov
- PR comments show coverage changes
- Coverage badges display status
- Historical tracking shows trends
- Can block PRs if coverage drops significantly

## Trace ID: 6
**Title:** Playwright E2E test configuration (separate system)

**Description:** TypeScript-based Playwright configuration for end-to-end browser testing, independent from pytest infrastructure

**Motivation:**
EduBoost V2 uses Playwright for end-to-end browser testing to validate complete user flows from UI to database. Playwright provides a separate testing infrastructure from pytest, optimized for browser automation with support for multiple browsers (Chromium, Firefox, WebKit) and devices (desktop, mobile). The TypeScript-based configuration enables type-safe test code and better IDE support. Playwright's browser matrix ensures cross-browser compatibility, while the retry strategy handles flaky tests in CI. This system complements pytest-based unit and integration tests by validating the application from the user's perspective, catching integration issues that unit tests might miss.

**Details:**
- **Execution Flow:** Playwright reads playwright.config.ts → Discovers tests in tests/e2e/ matching **/*.spec.ts → For each browser project: launches browser → Executes tests → Captures screenshots/videos on failure → Generates HTML report in playwright-report/ → Runs tests in parallel (workers) → Retries failed tests in CI (2 retries) → Reports results
- **Concurrency Safety:** Playwright runs tests in parallel with configurable workers. Each test gets isolated browser context. Browser instances are independent. No distributed locks needed as tests are isolated. Retry logic handles flaky tests by re-running failed tests
- **Covered Objects:** playwright.config.ts configuration, Test discovery (tests/e2e/, **/*.spec.ts), Browser projects (chromium, firefox, webkit, mobile), Execution strategy (timeout, retries, workers), Reporting (list, HTML), Test files (auth.spec.ts, diagnostic.spec.ts)
- **Timeouts:** Test discovery: ~100-500ms. Browser launch: ~1-3s. Test execution: ~5-30s per test. Report generation: ~100-500ms. Total E2E run: ~5-30min depending on test count and browser matrix
- **Migration Path:** From manual testing to Playwright E2E. Migration requires: 1) Install Playwright and browsers, 2) Create playwright.config.ts, 3) Write E2E tests in TypeScript, 4) Configure browser matrix, 5) Add Playwright to CI workflow, 6) Gradually increase test coverage
- **Error Handling:** Browser launch failures fail the test suite. Test failures captured with screenshots/videos. Retry logic handles flaky tests. Configuration errors fail with clear messages. All errors reported in HTML report and CI logs
- **Security Considerations:** E2E tests should use test credentials, not production credentials. Test data should not include sensitive information. Screenshots/videos should not be committed to git. Test environment should match production configuration. Browser automation should not expose secrets

**Trace text diagram:**
```
Playwright E2E Test Configuration
├── playwright.config.ts (root config file) <-- playwright.config.ts:30
│   ├── Test Discovery Settings
│   │   ├── testDir: "./tests/e2e" <-- 6a
│   │   └── testMatch: "**/*.spec.ts" <-- 6b
│   ├── Execution Strategy
│   │   ├── timeout: 60_000ms <-- playwright.config.ts:36
│   │   ├── retries: CI ? 2 : 0 <-- playwright.config.ts:40
│   │   └── workers: CI ? 2 : undefined <-- playwright.config.ts:40
│   ├── Browser Matrix
│   │   └── projects: [...] <-- playwright.config.ts:71
│   │       ├── chromium (Desktop Chrome) <-- playwright.config.ts:73
│   │       ├── firefox (Desktop Firefox) <-- playwright.config.ts:77
│   │       ├── webkit (Desktop Safari) <-- playwright.config.ts:81
│   │       ├── Mobile Chrome (Pixel 5) <-- playwright.config.ts:86
│   │       └── Mobile Safari (iPhone 13) <-- playwright.config.ts:90
│   └── Reporting
│       ├── list reporter <-- playwright.config.ts:47
│       └── html reporter (playwright-report/) <-- playwright.config.ts:48
└── tests/e2e/ (test files)
    └── auth.spec.ts <-- 6e
        ├── test("login flow")
        ├── test("registration flow")
        └── test("logout flow")
```

**Location ID: 6a**
- **Title:** E2E test directory
- **Description:** Configures Playwright to discover tests in tests/e2e/ directory
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/playwright.config.ts:32

**Location ID: 6b**
- **Title:** E2E test pattern
- **Description:** Matches TypeScript spec files for E2E test discovery
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/playwright.config.ts:33

**Location ID: 6c**
- **Title:** Browser matrix
- **Description:** Defines multiple browser projects (chromium, firefox, webkit, mobile)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/playwright.config.ts:71

**Location ID: 6d**
- **Title:** CI retry strategy
- **Description:** Retries flaky E2E tests twice in CI, zero retries locally
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/playwright.config.ts:43

**Location ID: 6e**
- **Title:** Example E2E test file
- **Description:** Actual Playwright test file for authentication flows
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/e2e/auth.spec.ts:1

### AI Guide: Playwright E2E Test Configuration

**Motivation:**
Playwright provides a separate TypeScript-based testing system for end-to-end browser testing. Unlike pytest, Playwright tests run in real browsers and validate complete user flows from UI to backend to ensure the application works as expected for end users.

**Details:**

**Playwright vs Pytest**
The comparison between Playwright E2E and pytest shows differences in language (TypeScript vs Python), execution (real browsers vs in-memory), scope (full user flows vs unit/integration), speed (slow seconds to minutes vs fast milliseconds), dependencies (running application stack vs database only), and use case (UI validation vs logic validation).

**Configuration Components**
Test discovery uses `testDir: "./tests/e2e"` for E2E test location and `testMatch: "**/*.spec.ts"` for file pattern discovery, separate from pytest test discovery with TypeScript files requiring compilation and naming convention like `auth.spec.ts`, `diagnostic.spec.ts` [6a-6b]. Execution strategy uses `timeout: 60_000ms` for global test timeout (60 seconds), `retries: process.env.CI ? 2 : 0` to retry flaky tests in CI, and `workers: process.env.CI ? 2 : undefined` to limit parallelism in CI, balancing speed with resource usage and preventing CI resource exhaustion.

**Browser Matrix**
The browser matrix includes Chromium for desktop Chrome (primary browser), Firefox for desktop Firefox (secondary browser), WebKit for desktop Safari (macOS/iOS rendering), and Mobile Chrome for Pixel 5 (Android testing) [6c]. This ensures cross-browser compatibility testing. Additional browsers include Mobile Safari for iPhone 13 (iOS testing) and the system can run all or subset based on CI constraints. Reporting uses the list reporter for console output during test run, the html reporter for interactive HTML report in playwright-report/, screenshots on failure, video recording (optional), and trace files for debugging.

**Running Playwright Tests:**

```bash
# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test auth.spec.ts

# Run in specific browser
npx playwright test --project=chromium

# Run in headed mode (show browser)
npx playwright test --headed

# Run in debug mode
npx playwright test --debug

# View HTML report
npx playwright show-report
```

**Test Structure:**

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('login flow', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'user@example.com');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('registration flow', async ({ page }) => {
    // Registration test implementation
  });

  test('logout flow', async ({ page }) => {
    // Logout test implementation
  });
});
```

**Fixtures and Page Objects:**

```typescript
// Built-in fixtures
{ page }      // Browser page
{ context }  // Browser context
{ browser }  // Browser instance

// Custom fixtures in tests/e2e/fixtures.ts
import { test as base } from '@playwright/test';

type TestFixtures = {
  authenticatedPage: Page;
};

const test = base.extend<TestFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // Login logic
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');
    await use(page);
  },
});
```

**CI Integration:**

```yaml
# GitHub Actions workflow
- name: Install Playwright
  run: npx playwright install --with-deps

- name: Run E2E tests
  run: npx playwright test
  env:
    CI: true

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## Trace ID: 7
**Title:** Module-specific fixture strategies for optional dependencies

**Description:** Specialized conftest.py in tests/unit/modules/diagnostics/ that gracefully skips tests when database is unavailable

**Motivation:**
EduBoost V2 implements module-specific fixture strategies to handle optional dependencies gracefully. Some modules (like diagnostics) have tests that can run with or without a database connection. The unit test conftest uses a graceful skip strategy, checking database availability and skipping tests if the database is unreachable. This allows developers to run unit tests without setting up a full database, while still enabling database tests when the database is available. The integration test conftest uses a hard-fail approach, requiring the database for integration tests. This dual strategy balances developer experience (tests run without dependencies) with CI requirements (comprehensive testing with dependencies).

**Details:**
- **Execution Flow:** Unit test conftest loads → _postgres_is_reachable() checks TCP connection to Postgres → db_available fixture calls reachability check → skip_if_no_db fixture skips tests if unavailable → db_session fixture depends on skip_if_no_db → Tests requiring database use db_session fixture → Tests skipped if database unavailable. Integration conftest loads → integration_engine fixture creates engine → Tests run or fail if database unavailable
- **Concurrency Safety:** Database reachability check is stateless and thread-safe. Socket connection attempts are independent per test. Fixture dependencies are resolved before test execution. No distributed locks needed as checks are independent. Multiple concurrent reachability checks are safe
- **Covered Objects:** _postgres_is_reachable() helper, db_available fixture, skip_if_no_db fixture, db_session fixture, integration_engine fixture, Socket connection attempts, Database engine creation, Test skip logic
- **Timeouts:** Reachability check: ~1s (socket timeout). Fixture resolution: <1ms. Test skip: <1ms. Integration engine creation: ~100-500ms. Overall impact on test execution is minimal
- **Migration Path:** From hard-fail to graceful skip. Migration requires: 1) Add reachability check helper, 2) Create db_available fixture, 3) Create skip_if_no_db fixture, 4) Update tests to use db_session fixture, 5) Keep integration tests with hard-fail approach
- **Error Handling:** Database unavailability in unit tests causes graceful skip with informative message. Database unavailability in integration tests causes hard failure. Socket connection errors logged. Invalid configuration causes fixture to fail with clear message
- **Security Considerations:** Reachability check should not expose database credentials. Test credentials should not be production credentials. Skip messages should not expose sensitive information. Database connection should use secure protocol. Test environment should match production configuration

**Trace text diagram:**
```
Module-Specific Fixture Strategy (Diagnostics)
├── Unit Test Conftest (Graceful Skip) <-- conftest.py:1
│   ├── _postgres_is_reachable() <-- 7a
│   │   └── socket.create_connection() <-- 7b
│   ├── db_available fixture <-- conftest.py:66
│   │   └── calls _postgres_is_reachable() <-- conftest.py:69
│   ├── skip_if_no_db fixture <-- 7c
│   │   └── pytest.skip() if unavailable <-- conftest.py:73
│   └── db_session fixture (opt-in) <-- conftest.py:90
│       └── depends on skip_if_no_db <-- conftest.py:91
└── Integration Test Conftest (Hard Fail) <-- conftest.py:1
    └── integration_engine fixture <-- conftest.py:29
        └── create_engine() no skip <-- 7e
```

**Location ID: 7a**
- **Title:** Database reachability check
- **Description:** Helper that tests TCP connection to Postgres before running tests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/modules/diagnostics/conftest.py:38

**Location ID: 7b**
- **Title:** Socket connection attempt
- **Description:** Attempts 1-second TCP connection to verify database availability
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/modules/diagnostics/conftest.py:44

**Location ID: 7c**
- **Title:** Conditional skip fixture
- **Description:** Opt-in fixture that skips tests when database is unreachable
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/modules/diagnostics/conftest.py:73

**Location ID: 7d**
- **Title:** Skip execution
- **Description:** Gracefully skips test with informative message instead of failing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/modules/diagnostics/conftest.py:84

**Location ID: 7e**
- **Title:** Integration hard-fail approach
- **Description:** Integration conftest creates engine without skip logic, hard-fails if DB unavailable
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/modules/diagnostics/conftest.py:32

### AI Guide: Module-Specific Fixture Strategies for Optional Dependencies

**Motivation:**
This trace demonstrates two contrasting strategies for handling optional dependencies in tests: graceful skipping in unit tests vs. hard failures in integration tests. The approach chosen depends on the test category and development workflow to optimize test execution and developer experience.

**Details:**

**Strategy Comparison**
The strategy comparison shows unit tests (graceful skip) with purpose to run tests when possible, skipping with message when DB unavailable, tests running locally without DB for developer experience, skipping in CI if DB not available, and use case for optional DB-dependent tests. Integration tests (hard fail) have purpose to ensure environment is ready, failing with error when DB unavailable, clear signal to start DB for developer experience, failing CI if DB not available, and use case for required DB-dependent tests.

**Unit Test Strategy (Graceful Skip)**
The database reachability check tests TCP connection to Postgres with a 1-second timeout for fast check, returns boolean for fixture logic, and has no SQLAlchemy dependency (lightweight) [7a-7b]. The DB available fixture is module-scoped for efficiency, caches result for all tests in module, and can be used directly or by other fixtures [7c]. The skip if no DB fixture is opt-in where tests must request this fixture, skips entire module if DB unavailable, provides clear message about why skipped, and suggests moving to integration tests [7c-7d]. The DB session fixture depends on skip_if_no_db and only creates session if DB available, so tests requesting db_session get automatic skip.

**Integration Test Strategy (Hard Fail)**
The integration test strategy has no reachability check, attempts connection directly, fails immediately if DB unavailable, provides clear signal that environment is misconfigured, and integration tests should run in proper environment. Use graceful skip for optional dependencies in unit tests when tests can run without the dependency, dependency is optional for development, want tests to run in CI even without DB, developers may not have DB running locally, tests are primarily logic-focused with optional DB validation, or module contains both DB-dependent and DB-independent tests. Use hard fail for required dependencies in integration tests when dependency is required for test execution, integration tests should guarantee environment is ready, want immediate feedback on environment issues, CI should fail if dependencies are missing, tests are specifically for integration validation, or environment should be controlled (Docker, CI). Best practices include providing clear skip messages explaining why tests were skipped, suggesting alternative test locations in skip messages, keeping reachability checks lightweight (TCP socket, not full connection), using appropriate fixture scope (module for efficiency, function for isolation), documenting fixture behavior in docstrings, and considering environment variables for controlling skip behavior.
- **Tests never skipping:** Verify reachability check is correct
- **Flaky reachability:** Increase timeout or check multiple times
- **Silent failures:** Ensure skip messages are informative
- **Fixture not skipping:** Check fixture dependencies and scope

**Advanced Patterns:**

```python
# Environment-controlled skip
@pytest.fixture
def skip_if_no_db():
    if os.environ.get("REQUIRE_DB") == "true" and not _postgres_is_reachable():
        pytest.skip("DB required but not available")

# Retry reachability check
@pytest.fixture
def db_available_with_retry():
    for _ in range(3):
        if _postgres_is_reachable():
            return True
        time.sleep(1)
    return False

# Multiple dependency checks
@pytest.fixture
def skip_if_dependencies_missing():
    missing = []
    if not _postgres_is_reachable():
        missing.append("Postgres")
    if not _redis_is_reachable():
        missing.append("Redis")
    if missing:
        pytest.skip(f"Missing dependencies: {', '.join(missing)}")
```

**Testing Fixture Behavior:**

```python
# Test that skip fixture works
def test_skip_if_no_db_skips_when_unavailable(monkeypatch):
    monkeypatch.setattr("socket.create_connection", side_effect=OSError)
    with pytest.raises(pytest.skip.Exception):
        skip_if_no_db()
```

---

## Code snippets from Codemap files

### File: /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/modules/diagnostics/conftest.py

Lines: 30-34
```python
def integration_engine():
    """Session-scoped engine – created once per pytest session."""
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    yield engine
    engine.dispose()
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini

Lines: 8-15
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
norecursedirs = .* build dist CVS _darcs {arch} *.egg .venv venv node_modules...
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

Lines: 17-35
```ini
# ── Coverage ──────────────────────────────────────────────────────────────────
addopts =
    --strict-markers
    --tb=short
    --cov=app
    --cov-report=term-missing
    --cov-report=html:coverage_html
    --cov-report=xml:coverage.xml
    --cov-fail-under=80

# ── Markers ───────────────────────────────────────────────────────────────────
markers =
    unit: fast, isolated unit tests (no I/O)
    integration: tests that require a live DB or Redis
    e2e: end-to-end tests via Playwright (require running stack)
    slow: tests that take >5 seconds
    llm: tests that make real LLM API calls (skipped in CI unless ALLOW_LLM_T...
    performance: performance/SLO checks that may require a seeded database or...
    smoke: smoke / critical-path tests
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/conftest.py

Lines: 3-7
```python
import pytest
pytestmark = pytest.mark.integration
```

Lines: 10-14
```python
@pytest_asyncio.fixture(scope="session", autouse=True)
async def integration_db(test_db_setup):
    """Automatically create and tear down the test database schema for integr...
    yield
```

Lines: 93-97
```python
    import app.core.refresh_tokens as refresh_tokens_module

    monkeypatch.setattr(redis_module, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(refresh_tokens_module, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(redis_module, "_pool", fake_redis)
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/tests/smoke/test_content_factory_admin_api_smoke.py

Lines: 6-10
```python
from fastapi.testclient import TestClient

pytestmark = pytest.mark.smoke

class TestContentFactoryAdminAPISmoke:
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/.gitignore

Lines: 9-13
```
**/__pycache__/
*.py[cod]
coverage_html/
node_modules/
.next/
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-core.yml

Lines: 85-91
```yaml
      - name: Unit tests
        run: pytest -c pytest.ini tests/unit -q --no-cov

      - name: Integration tests
        run: pytest -c pytest.ini tests/integration -q --no-cov
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml

Lines: 11-15
```yaml
env:
  PYTHON_VERSION: "3.12.3"
  COVERAGE_THRESHOLD: "60"
  V2_ENTRYPOINT: "app.api_v2:app"
```

Lines: 151-155
```yaml
        run: |
          pytest tests/ \
            --cov=app \
            --cov-report=xml \
            --cov-report=term-missing \
```

Lines: 158-162
```yaml
      - name: Upload coverage report
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/playwright.config.ts

Lines: 30-35
```typescript
export default defineConfig({
  // ── Test discovery ──────────────────────────────────────────────────────...
  testDir: "./tests/e2e",
  testMatch: ["**/*.spec.ts"],

  // ── Global test timeout (ms) ───────────────────────────────────────────────
```

Lines: 41-45
```typescript
  // ── Retry logic ─────────────────────────────────────────────────────────...
  retries: process.env.CI ? 2 : 0,

  // ── Reporting ───────────────────────────────────────────────────────────...
```

Lines: 69-73
```typescript
  // ── Browser projects ────────────────────────────────────────────────────...
  projects: [
    {
      name:  "chromium",
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/modules/diagnostics/conftest.py

Lines: 36-40
```python
# ---------------------------------------------------------------------------

def _postgres_is_reachable() -> bool:
    """Return True when a TCP connection to the configured Postgres host/port
    succeeds within 1 second."""
```

Lines: 42-46
```python
    port = int(os.environ.get("PGPORT", "5432"))
    try:
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except OSError:
```

Lines: 71-75
```python
@pytest.fixture(scope="module")
def skip_if_no_db(db_available: bool) -> None:
    """Opt-in fixture: skip the entire module when Postgres is absent.
```

Lines: 82-86
```python
    """
    if not db_available:
        pytest.skip(
            "Postgres not reachable – skipping DB-dependent test "
            "(move to tests/integration/ for guaranteed execution)."
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/tests/conftest.py

Lines: 30-34
```python

@pytest_asyncio.fixture(scope="session")
async def test_db_setup():
    """Ensure a clean database schema for tests that request database access."""
```

Lines: 42-47
```python
    try:
        await drop_all_tables()
        await create_all_tables()
    except (OSError, SQLAlchemyError) as exc:
        if _require_test_database():
```

Lines: 55-59
```python

@pytest_asyncio.fixture
async def db_session(test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """Provide a fresh async database session for each test."""
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/tests/e2e/auth.spec.ts

Lines: 1-3
```typescript
/**
 * tests/e2e/auth.spec.ts — EduBoost SA V2
 *
```
