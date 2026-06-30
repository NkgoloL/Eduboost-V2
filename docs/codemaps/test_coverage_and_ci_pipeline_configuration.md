# Test Coverage and CI Pipeline Configuration

Maps pytest configuration, coverage reporting, and CI execution across the EduBoost-V2 testing infrastructure. Key entry points include pytest configuration [1a], coverage threshold enforcement [2b], CI unit test execution [3c], integration test database setup [4b], and contract smoke test validation [5d].

## Trace ID: 1
**Title:** Pytest Configuration and Test Discovery

**Description:** Core pytest setup defining test paths, markers, and asyncio mode for test execution

**Motivation:**
EduBoost V2 uses pytest as its primary test framework with centralized configuration in pytest.ini. The configuration enables automatic async test detection without requiring decorators, essential for testing FastAPI endpoints and async database operations. Test discovery is restricted to the tests/ directory with specific naming patterns (test_*.py, Test*, test_*) to prevent accidental collection of non-test files. Custom markers (unit, integration, e2e, llm, smoke) enable selective test execution based on test characteristics, allowing developers to run fast unit tests during development and conditionally skip expensive tests like LLM API calls in CI. The conftest.py file ensures repository root is on sys.path for consistent imports and sets the test environment before any imports, ensuring tests run in a controlled environment.

**Details:**
- **Execution Flow:** pytest.ini configuration → asyncio_mode = auto → testpaths = tests → markers definition → llm marker (conditional skip) → tests/conftest.py session setup → ensure_repo_root_on_path() → sys.path.insert(0, repo_root) → os.environ["APP_ENV"] = "test" → Test discovery and execution → Collect tests from tests/ → Apply markers (unit/integration/e2e) → Run with asyncio auto-detection
- **Concurrency Safety:** pytest test collection is sequential. Test execution can be parallelized with pytest-xdist. Async tests run in event loop managed by pytest-asyncio. No distributed locks needed as tests are isolated. Environment setup happens once per session
- **Covered Objects:** pytest.ini configuration, asyncio mode, test discovery patterns, marker definitions, conftest.py session setup, sys.path manipulation, environment variables, test collection, marker application
- **Timeouts:** pytest.ini parsing: <1ms. Test collection: ~100-500ms depending on test count. Environment setup: ~1-5ms. Async test setup: ~10-50ms per test. Overall test execution varies by test category
- **Migration Path:** From unittest or nose to pytest. Migration requires: 1) Create pytest.ini with configuration, 2) Rename test files to test_*.py pattern, 3) Convert test methods to pytest format, 4) Add pytest-asyncio for async tests, 5) Add conftest.py for session setup, 6) Update CI to use pytest
- **Error Handling:** Invalid pytest.ini syntax causes pytest to fail with clear error message. Missing pytest-asyncio causes async tests to fail. Unregistered markers with --strict-markers cause warnings. Invalid test discovery patterns result in no tests collected. Environment setup failures logged
- **Security Considerations:** pytest.ini should not contain secrets. Test discovery patterns should not accidentally collect sensitive files. Environment variables should not expose production credentials. Marker names should not expose internal implementation details. Test environment should be isolated from production

**Trace text diagram:**
```
Pytest Test Execution Flow
├── pytest.ini configuration <-- 1a, 1b
│   ├── asyncio_mode = auto <-- 1a
│   ├── testpaths = tests <-- 1b
│   └── markers definition <-- 1c
│       └── llm marker (conditional skip) <-- 1d
├── tests/conftest.py session setup <-- conftest.py:1
│   ├── ensure_repo_root_on_path() <-- 1e
│   │   └── sys.path.insert(0, repo_root) <-- conftest.py:19
│   └── os.environ["APP_ENV"] = "test" <-- 1f
└── Test discovery and execution
    ├── Collect tests from tests/
    ├── Apply markers (unit/integration/e2e)
    └── Run with asyncio auto-detection
```

**Location ID: 1a**
- **Title:** Asyncio auto mode enabled
- **Description:** Automatically detects and runs async test functions without explicit decorator
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:10

**Location ID: 1b**
- **Title:** Test discovery root
- **Description:** Pytest searches for tests starting from the tests/ directory
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:11

**Location ID: 1c**
- **Title:** Test marker registration
- **Description:** Defines custom markers for categorizing tests by type and execution requirements
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:28

**Location ID: 1d**
- **Title:** LLM test marker
- **Description:** Expensive tests requiring real API calls are skipped by default in CI
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:33

**Location ID: 1e**
- **Title:** Repository path setup
- **Description:** Ensures repository root is on sys.path for consistent imports
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/conftest.py:15

**Location ID: 1f**
- **Title:** Test environment configuration
- **Description:** Sets environment to test mode before any imports
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/conftest.py:22

### AI Guide: Pytest Configuration and Test Discovery

**Motivation:**
The pytest configuration centralizes test execution behavior, async support, and test discovery paths. This configuration ensures that async tests run correctly, test discovery is restricted to the appropriate directories, and custom markers enable selective test execution.

**Details:**

**Async Support and Discovery**
Asyncio auto mode enables automatic async test detection without requiring decorators, which is essential for FastAPI and async database tests [1a]. The test discovery root restricts discovery to the tests/ directory to prevent accidental collection of non-test files [1b].

**Markers and Path Setup**
Test marker registration defines custom markers for test categorization, enabling selective test execution [1c]. The LLM test marker marks expensive API tests that are conditionally skipped in CI to prevent API key exposure [1d]. Repository path setup ensures the repo root is on sys.path for consistent imports and critical module resolution [1e].

**Environment Configuration**
The test environment configuration sets APP_ENV to test to ensure a controlled test environment before imports [1f]. This ensures that all tests run in a predictable environment with known configuration.

## Trace ID: 2
**Title:** Coverage Collection and Threshold Enforcement

**Description:** Pytest-cov plugin configuration for measuring code coverage and enforcing quality gates

**Motivation:**
EduBoost V2 uses pytest-cov to measure code coverage and enforce quality gates. Coverage measurement ensures that code changes are adequately tested, preventing regressions and maintaining code quality. The configuration enables multiple report formats (terminal, HTML, XML) for different use cases: terminal for immediate feedback during development, HTML for detailed interactive browsing, and XML for CI integration with tools like Codecov. The coverage threshold (--cov-fail-under=80) enforces a minimum coverage level, failing the test run if coverage falls below the threshold. This automated quality gate prevents code with insufficient test coverage from being merged. The addopts section applies these settings to every pytest invocation, ensuring consistent coverage measurement across all test runs.

**Details:**
- **Execution Flow:** pytest.ini (configuration file) → [pytest] section → --cov=app → --cov-report=term-missing → --cov-report=html:coverage_html → --cov-report=xml:coverage.xml → --cov-fail-under=80 → addopts (automatic options) → Applied to every pytest invocation → pytest-cov plugin (runtime) → Coverage.py measurement engine → Collects line/branch coverage data → Report generators → Terminal formatter (shows missing lines) → HTML builder (browsable report) → XML exporter (CI integration) → Threshold validator → Exits with error if < 80%
- **Concurrency Safety:** Coverage collection is thread-safe with pytest-xdist. Each worker collects coverage independently. Coverage data merged at end of test run. No distributed locks needed. Coverage instrumentation has minimal performance impact (~10-20% overhead)
- **Covered Objects:** pytest.ini configuration, pytest-cov plugin, Coverage.py measurement engine, Report generators, Terminal formatter, HTML builder, XML exporter, Threshold validator, Coverage data structures
- **Timeouts:** Coverage instrumentation: ~10-50ms overhead per test. Report generation: ~100-500ms. Total coverage overhead: ~10-20% of test execution time
- **Migration Path:** From no coverage to coverage measurement. Migration requires: 1) Install pytest-cov, 2) Add --cov=app to pytest.ini addopts, 3) Configure report formats, 4) Set initial low threshold, 5) Gradually increase threshold as coverage improves, 6) Add coverage_html/ to .gitignore
- **Error Handling:** Coverage instrumentation failures logged but don't block tests. Report generation failures logged. Threshold failures fail test run with clear message. Invalid coverage configuration causes pytest to fail with error
- **Security Considerations:** Coverage reports should not be committed to git (HTML reports in .gitignore). Coverage data should not include sensitive information from tests. Coverage thresholds should be realistic and achievable. Coverage reports should not expose internal implementation details publicly

**Trace text diagram:**
```
Pytest Configuration & Coverage Collection
├── pytest.ini (configuration file) <-- pytest.ini:1
│   ├── [pytest] section <-- pytest.ini:9
│   │   ├── --cov=app <-- 2a
│   │   ├── --cov-report=term-missing <-- 2c
│   │   ├── --cov-report=html:coverage_html <-- 2d
│   │   ├── --cov-report=xml:coverage.xml <-- 2e
│   │   └── --cov-fail-under=80 <-- 2b
│   └── addopts (automatic options) <-- pytest.ini:18
│       └── Applied to every pytest invocation
└── pytest-cov plugin (runtime)
    ├── Coverage.py measurement engine
    │   └── Collects line/branch coverage data
    ├── Report generators
    │   ├── Terminal formatter (shows missing lines)
    │   ├── HTML builder (browsable report)
    │   └── XML exporter (CI integration)
    └── Threshold validator
        └── Exits with error if < 80%
```

**Location ID: 2a**
- **Title:** Coverage measurement scope
- **Description:** Measures coverage for all code in the app/ package
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:21

**Location ID: 2b**
- **Title:** Coverage threshold gate
- **Description:** Fails test run if coverage drops below 80% threshold
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:25

**Location ID: 2c**
- **Title:** Terminal coverage report
- **Description:** Shows missing lines in terminal output for quick feedback
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:22

**Location ID: 2d**
- **Title:** HTML coverage report
- **Description:** Generates browsable HTML report in coverage_html/ directory
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:23

**Location ID: 2e**
- **Title:** XML coverage export
- **Description:** Exports coverage data for CI tools and codecov integration
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:24

### AI Guide: Coverage Collection and Threshold Enforcement

**Motivation:**
Coverage configuration ensures code quality by measuring how much of the codebase is exercised by tests. The pytest-cov plugin integrates coverage collection with test execution, providing multiple report formats and threshold enforcement to prevent coverage regression.

**Details:**

**Measurement and Thresholds**
The coverage measurement scope measures coverage for the app/ package while excluding test code to focus on production code quality [2a]. The coverage threshold gate fails the test run if coverage is below 80%, enforcing a minimum coverage quality gate to prevent coverage regression [2b].

**Report Generation**
The terminal coverage report shows coverage in the terminal with highlighted missing lines for immediate feedback [2c]. The HTML coverage report generates browsable HTML with interactive source highlighting for detailed analysis [2d]. The XML coverage export exports coverage data for CI, used by Codecov to enable tracking over time [2e].

## Trace ID: 3
**Title:** CI Core Unit Test Execution

**Description:** GitHub Actions workflow executing unit tests with coverage disabled for fast feedback

**Motivation:**
EduBoost V2 uses GitHub Actions CI workflows to automate test execution with different strategies for different needs. The ci-core.yml workflow provides fast feedback by running unit and integration tests separately with coverage disabled, optimizing for speed during development cycles. The workflow spins up PostgreSQL and Redis service containers for integration tests, ensuring tests run against real services. Environment variables configure database connections, Redis URLs, and JWT secrets for the test environment. Dependencies are installed from requirements/dev.txt. Unit tests run with --no-cov flag for speed, while integration tests run against live database services. This separation allows developers to get quick feedback on unit tests while still validating integration with real services.

**Details:**
- **Execution Flow:** CI Core Workflow (ci-core.yml) → Workflow Trigger (PR/push to master) → Job: core → Services Setup → PostgreSQL container → Health check (pg_isready) → Redis container → Health check (redis-cli ping) → Environment Configuration → DATABASE_URL env var → REDIS_URL env var → JWT_SECRET env var → Dependencies Installation → pip install -r requirements/dev.txt → Test Execution Steps → Unit tests → Integration tests
- **Concurrency Safety:** CI jobs run in isolated containers. Service containers are isolated per job. Test execution is sequential within job. No distributed locks needed. Multiple jobs can run in parallel
- **Covered Objects:** GitHub Actions workflow, service containers, health checks, environment variables, dependency installation, pytest execution, unit tests, integration tests
- **Timeouts:** Service container startup: ~10-30s. Health checks: ~5-10s. Dependency installation: ~30-60s. Unit tests: ~30-120s. Integration tests: ~60-180s. Total workflow: ~2-5min
- **Migration Path:** From manual testing to CI automation. Migration requires: 1) Create GitHub Actions workflow, 2) Add service containers, 3) Configure environment variables, 4) Add test execution steps, 5) Enable workflow on PR/push
- **Error Handling:** Service container failures fail the job. Health check failures fail the job. Dependency installation failures fail the job. Test failures fail the job with logs. All errors reported in GitHub Actions UI
- **Security Considerations:** Test credentials should not be production credentials. Environment variables should not contain secrets. Service containers should use official images. JWT secrets should be test-only. Database should be isolated per job

**Trace text diagram:**
```
CI Core Workflow (ci-core.yml) <-- ci-core.yml:1
├── Workflow Trigger (PR/push to master) <-- ci-core.yml:3
│   └── Job: core <-- ci-core.yml:18
│       ├── Services Setup <-- ci-core.yml:23
│       │   ├── PostgreSQL container <-- 3a
│       │   │   └── Health check (pg_isready) <-- ci-core.yml:33
│       │   └── Redis container <-- ci-core.yml:37
│       │       └── Health check (redis-cli ping) <-- ci-core.yml:42
│       ├── Environment Configuration <-- ci-core.yml:47
│       │   ├── DATABASE_URL env var <-- 3b
│       │   ├── REDIS_URL env var <-- ci-core.yml:51
│       │   └── JWT_SECRET env var <-- ci-core.yml:54
│       ├── Dependencies Installation <-- ci-core.yml:68
│       │   └── pip install -r requirements/dev.txt <-- ci-core.yml:72
│       └── Test Execution Steps <-- ci-core.yml:58
│           ├── Unit tests <-- 3c
│           └── Integration tests <-- 3d
```

**Location ID: 3a**
- **Title:** PostgreSQL service container
- **Description:** Spins up Postgres 16 for integration tests requiring database
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-core.yml:24

**Location ID: 3b**
- **Title:** Test database connection
- **Description:** Configures async PostgreSQL connection for test environment
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-core.yml:50

**Location ID: 3c**
- **Title:** Unit test execution
- **Description:** Runs unit tests with coverage disabled for speed
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-core.yml:87

**Location ID: 3d**
- **Title:** Integration test execution
- **Description:** Runs integration tests against live database services
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-core.yml:90

### AI Guide: CI Core Unit Test Execution

**Motivation:**
The CI core workflow provides fast feedback by running unit and integration tests with coverage disabled. Using service containers for dependencies and separating unit from integration tests ensures reliable execution while keeping workflow time minimal.

**Details:**

**Service Container Setup**
The PostgreSQL service container spins up Postgres 16 for integration tests using the official Docker image [3a]. A health check ensures the database is ready before tests run. The test database connection configures an async PostgreSQL connection using environment variables to connect to the service container [3b].

**Test Execution**
Unit test execution runs unit tests with --no-cov for speed optimization and fast feedback [3c]. Integration test execution runs integration tests against live services to validate component interactions using real database and Redis [3d]. This separation allows unit tests to run quickly while integration tests validate real-world interactions.

## Trace ID: 4
**Title:** Integration Test Database Fixture Setup

**Description:** Session-scoped database fixtures providing clean schema for integration tests

**Motivation:**
EduBoost V2 uses a hierarchical fixture system to manage database test isolation and lifecycle for integration tests. Session-scoped fixtures (test_db_setup) run once per test session to create the database schema, optimizing performance by avoiding repeated schema creation. Function-scoped fixtures (db_session) provide fresh database sessions for each test, ensuring test isolation by rolling back transactions after each test. The integration marker is automatically applied to all tests in the integration/ directory via pytestmark at the module level. Redis patching uses autouse fixture to automatically replace real Redis with in-memory fake for integration tests, avoiding external dependencies. This system enables fast, reliable database testing with real database connections while maintaining test isolation.

**Details:**
- **Execution Flow:** Test Collection Phase → conftest.py auto-discovery → pytestmark = integration → Session Fixture Initialization → integration_db() fixture → depends on test_db_setup → test_db_setup (session scope) → drop_all_tables() → create_all_tables() → yield (tests run here) → cleanup: drop_all_tables() → Test Function Fixtures → patch_redis() autouse fixture → monkeypatch.setattr() → db_session() per-test fixture → AsyncSessionFactory() context
- **Concurrency Safety:** Session-scoped fixtures run once before parallel test execution. Function-scoped fixtures are independent per test. Database transactions provide isolation between tests. Redis patching uses monkeypatch for thread-safe replacement. No distributed locks needed as tests are isolated
- **Covered Objects:** Integration marker, session fixtures, database schema creation, table dropping, Redis patching, monkeypatch, AsyncSessionFactory, test isolation
- **Timeouts:** Session setup (drop/create tables): ~1-5s. Function-scoped session creation: ~10-50ms. Test execution: varies by test. Session cleanup: ~10-50ms. Overall test session: depends on test count
- **Migration Path:** From ad-hoc database setup to fixture-based system. Migration requires: 1) Create conftest.py with session-scoped fixture, 2) Add function-scoped session fixture, 3) Add integration marker, 4) Add Redis patching, 5) Update tests to use fixtures
- **Error Handling:** Database connection failures cause fixture to fail and tests to skip. Schema creation failures fail the test session. Session cleanup failures logged but don't block test completion. Redis patching failures fail affected tests
- **Security Considerations:** Test database should be separate from production database. Test credentials should not be production credentials. Database schema in tests should match production schema. Redis patching should not affect production Redis

**Trace text diagram:**
```
Integration Test Database Setup
├── Test Collection Phase
│   └── conftest.py auto-discovery
│       └── pytestmark = integration <-- 4a
├── Session Fixture Initialization
│   ├── integration_db() fixture <-- 4b
│   │   └── depends on test_db_setup <-- conftest.py:12
│   │       └── (from tests/conftest.py)
│   └── test_db_setup (session scope) <-- conftest.py:32
│       ├── drop_all_tables() <-- 4c
│       ├── create_all_tables() <-- 4d
│       └── yield (tests run here) <-- conftest.py:52
│           └── cleanup: drop_all_tables() <-- conftest.py:54
└── Test Function Fixtures
    ├── patch_redis() autouse fixture <-- 4e
    │   └── monkeypatch.setattr() <-- conftest.py:95
    └── db_session() per-test fixture <-- conftest.py:57
        └── AsyncSessionFactory() context <-- conftest.py:60
```

**Location ID: 4a**
- **Title:** Integration marker auto-apply
- **Description:** Automatically marks all tests in integration/ as integration tests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/conftest.py:5

**Location ID: 4b**
- **Title:** Integration DB fixture
- **Description:** Session-scoped fixture ensuring database schema exists for all integration tests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/conftest.py:12

**Location ID: 4c**
- **Title:** Clean database state
- **Description:** Drops all tables before test session to ensure clean state
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/conftest.py:44

**Location ID: 4d**
- **Title:** Schema creation
- **Description:** Creates fresh database schema from SQLAlchemy models
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/conftest.py:45

**Location ID: 4e**
- **Title:** Redis mock injection
- **Description:** Patches Redis client with in-memory fake for integration tests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/conftest.py:90

### AI Guide: Integration Test Database Fixture Setup

**Motivation:**
The fixture hierarchy provides clean database state for integration tests while optimizing performance through session-level schema setup. This pattern ensures test isolation with real database connections by using session-scoped fixtures for expensive setup and function-scoped fixtures for test isolation.

**Details:**

**Marker and Fixture Setup**
The integration marker auto-apply automatically marks all tests in the integration/ directory using a module-level pytestmark, eliminating the need for manual marker application [4a]. The integration DB fixture is a session-scoped fixture for schema setup that depends on root test_db_setup to ensure the schema exists for all tests [4b].

**Database State**
The clean database state drops all tables before the session to ensure a clean starting state and prevent data leakage between sessions [4c]. Schema creation creates a fresh schema from models using SQLAlchemy metadata to match the production schema [4d].

**Redis Mocking**
The Redis mock injection patches Redis with an in-memory fake using an autouse fixture that applies automatically, eliminating the need for external Redis [4e]. This allows integration tests to run without external dependencies while still testing Redis interactions.

## Trace ID: 5
**Title:** Contract Smoke Test Validation

**Description:** FastAPI TestClient-based smoke tests validating router registration and OpenAPI contracts

**Motivation:**
EduBoost V2 uses contract smoke tests to validate that FastAPI routers are correctly registered and expose the expected endpoints in the OpenAPI schema. These tests use FastAPI's TestClient to make HTTP requests without network overhead, enabling fast validation of API contracts. The tests verify that endpoints exist in the OpenAPI schema and return expected HTTP status codes. This approach catches configuration errors, missing route registrations, and broken contracts early in the development cycle. The TestClient fixture wraps the FastAPI app for synchronous test requests, simulating HTTP calls without requiring a running server. Multiple router test classes (SystemRouter, ConsentRouter, PopiaRouter, AuthRouter, etc.) ensure comprehensive coverage of all API endpoints.

**Details:**
- **Execution Flow:** Test Module Setup → @pytest.fixture client() → return TestClient(app) → Test Execution → TestSystemRouter class → test_health_endpoint_exists_in_openapi() → schema = client.app.openapi() → assert "/api/v2/system/health" in schema["paths"] → test_health_endpoint_returns_200() → response = client.get("/api/v2/system/health") → assert response.status_code == 200 → Other Router Test Classes → TestConsentRouter → TestPopiaRouter → TestAuthRouter → [10+ more router test classes]
- **Concurrency Safety:** TestClient is stateless and thread-safe. Each test gets independent client instance. No shared state between tests. No distributed locks needed. Tests can run in parallel
- **Covered Objects:** TestClient fixture, FastAPI app, OpenAPI schema, router registration, HTTP requests, response validation, contract tests, smoke tests
- **Timeouts:** TestClient instantiation: ~1-5ms. OpenAPI schema generation: ~10-50ms. HTTP request execution: ~10-50ms. Response validation: ~1-5ms. Total per test: ~20-110ms
- **Migration Path:** From manual API testing to contract tests. Migration requires: 1) Create TestClient fixture, 2) Write smoke tests for each router, 3) Validate OpenAPI schema, 4) Test HTTP responses, 5) Add to CI pipeline
- **Error Handling:** App import failures fail fixture. OpenAPI generation failures fail tests. HTTP request failures fail tests. Response validation failures fail tests. All errors reported with clear messages
- **Security Considerations:** TestClient does not make network calls. No sensitive data in test requests. No authentication required for smoke tests. Test environment should be isolated. No production data used

**Trace text diagram:**
```
Contract Smoke Test Validation Flow
├── Test Module Setup
│   └── @pytest.fixture client() <-- 5a
│       └── return TestClient(app) <-- 5b
│
└── Test Execution
    ├── TestSystemRouter class <-- test_api_v2_routers_contract_smoke.py:25
    │   ├── test_health_endpoint_exists_in_openapi() <-- test_api_v2_routers_contract_smoke.py:28
    │   │   └── schema = client.app.openapi() <-- 5c
    │   │       └── assert "/api/v2/system/health"
    │   │           in schema["paths"] <-- 5d
    │   │
    │   └── test_health_endpoint_returns_200() <-- test_api_v2_routers_contract_smoke.py:53
    │       └── response = client.get(
    │           "/api/v2/system/health") <-- 5e
    │           └── assert response.status_code
    │               == 200 <-- 5f
    │
    └── Other Router Test Classes
        ├── TestConsentRouter <-- test_api_v2_routers_contract_smoke.py:74
        ├── TestPopiaRouter <-- test_api_v2_routers_contract_smoke.py:93
        ├── TestAuthRouter <-- test_api_v2_routers_contract_smoke.py:112
        └── [10+ more router test classes]
```

**Location ID: 5a**
- **Title:** TestClient fixture
- **Description:** Creates FastAPI TestClient for making HTTP requests without network
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/test_api_v2_routers_contract_smoke.py:20

**Location ID: 5b**
- **Title:** TestClient instantiation
- **Description:** Wraps FastAPI app for synchronous test requests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/test_api_v2_routers_contract_smoke.py:22

**Location ID: 5c**
- **Title:** OpenAPI schema generation
- **Description:** Generates OpenAPI schema from registered routes for validation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/test_api_v2_routers_contract_smoke.py:30

**Location ID: 5d**
- **Title:** Route registration validation
- **Description:** Verifies health endpoint is exposed in OpenAPI schema
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/test_api_v2_routers_contract_smoke.py:31

**Location ID: 5e**
- **Title:** HTTP request execution
- **Description:** Makes actual HTTP GET request through TestClient
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/test_api_v2_routers_contract_smoke.py:55

**Location ID: 5f**
- **Title:** Response validation
- **Description:** Asserts endpoint returns successful HTTP status
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/test_api_v2_routers_contract_smoke.py:56

### AI Guide: Contract Smoke Test Validation

**Motivation:**
Contract smoke tests validate that FastAPI routers are correctly registered and expose expected endpoints. Using TestClient-based tests validates API contracts without network overhead, ensuring that routers are properly included and endpoints are accessible.

**Details:**

**TestClient Setup**
The TestClient fixture creates a FastAPI TestClient that enables HTTP requests without network overhead by wrapping the app for synchronous calls [5a]. The TestClient instantiation instantiates TestClient with the app and returns a client instance used by all tests [5b].

**Schema Validation**
OpenAPI schema generation generates the schema from routes to validate endpoint registration and check contract compliance [5c]. Route registration validation verifies that the endpoint exists in the schema, checks that the path exists, and validates HTTP methods [5d].

**Request and Response Validation**
HTTP request execution makes a GET request through TestClient to simulate an HTTP call without network overhead [5e]. Response validation asserts the HTTP status code, validates the response, and checks contract compliance [5f]. This ensures that endpoints respond correctly to requests.

## Trace ID: 6
**Title:** CI Coverage Threshold Enforcement

**Description:** Main CI/CD workflow enforcing coverage thresholds and uploading reports to Codecov

**Motivation:**
EduBoost V2 uses the main CI/CD workflow to enforce coverage thresholds and upload coverage reports to Codecov for tracking over time. The workflow defines a COVERAGE_THRESHOLD environment variable (60%) that is more lenient than the local threshold (80%) to accommodate PRs while still maintaining quality standards. The pytest invocation runs the full test suite with coverage measurement enabled, generating XML and terminal reports. The --cov-fail-under flag uses the environment variable to enforce the threshold, failing the CI build if coverage falls below 60%. The Codecov action uploads the coverage.xml file to Codecov for visualization and historical tracking. This system ensures code quality is maintained in CI while providing visibility into coverage trends over time.

**Details:**
- **Execution Flow:** CI/CD Pipeline - Unit Test Job → Workflow Configuration → Environment Variables → COVERAGE_THRESHOLD: "60" → Unit Test Execution Step → pytest invocation → Coverage measurement → --cov=app flag → Coverage reporting → --cov-report=xml → --cov-report=term-missing → Threshold enforcement → --cov-fail-under=$THRESHOLD → Artifact Upload Step → Codecov Action → Upload coverage.xml
- **Concurrency Safety:** Coverage collection is thread-safe. CI job runs in isolated environment. Threshold enforcement is deterministic. No distributed locks needed. Coverage upload happens after tests complete
- **Covered Objects:** CI/CD workflow, environment variables, pytest invocation, coverage measurement, coverage reporting, threshold enforcement, Codecov action, coverage artifacts
- **Timeouts:** Environment setup: ~10-30s. Test execution with coverage: ~2-5min. Report generation: ~100-500ms. Codecov upload: ~10-30s. Total job: ~2-6min
- **Migration Path:** From no CI coverage to CI enforcement. Migration requires: 1) Add coverage to CI workflow, 2) Set environment variable for threshold, 3) Configure pytest with coverage flags, 4) Add Codecov action, 5) Enable workflow on PR/push
- **Error Handling:** Coverage below threshold fails job. Codecov upload failures logged but don't fail job. Test failures fail job with logs. All errors reported in GitHub Actions UI
- **Security Considerations:** Coverage reports should not contain sensitive data. Codecov token should be stored in secrets. Threshold should be realistic. Coverage data should not expose implementation details publicly

**Trace text diagram:**
```
CI/CD Pipeline - Unit Test Job
├── Workflow Configuration
│   └── Environment Variables <-- ci-cd.yml:11
│       └── COVERAGE_THRESHOLD: "60" <-- 6a
├── Unit Test Execution Step <-- ci-cd.yml:150
│   ├── pytest invocation <-- 6b
│   ├── Coverage measurement
│   │   └── --cov=app flag <-- 6c
│   ├── Coverage reporting
│   │   ├── --cov-report=xml <-- ci-cd.yml:154
│   │   └── --cov-report=term-missing <-- ci-cd.yml:155
│   └── Threshold enforcement
│       └── --cov-fail-under=$THRESHOLD <-- 6d
└── Artifact Upload Step <-- ci-cd.yml:159
    └── Codecov Action <-- 6e
        └── Upload coverage.xml <-- 6f
```

**Location ID: 6a**
- **Title:** Coverage threshold variable
- **Description:** Defines minimum acceptable coverage percentage for CI
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:13

**Location ID: 6b**
- **Title:** Full test suite execution
- **Description:** Runs all tests with coverage measurement enabled
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:152

**Location ID: 6c**
- **Title:** Coverage scope definition
- **Description:** Measures coverage for app package during test execution
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:153

**Location ID: 6d**
- **Title:** Threshold enforcement
- **Description:** Fails CI build if coverage falls below 60% threshold
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:156

**Location ID: 6e**
- **Title:** Codecov upload
- **Description:** Uploads coverage.xml to Codecov for tracking and visualization
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:160

**Location ID: 6f**
- **Title:** Coverage artifact
- **Description:** Specifies XML coverage report for external analysis
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:162

### AI Guide: CI Coverage Threshold Enforcement

**Motivation:**
The CI workflow enforces coverage thresholds and uploads reports to Codecov for tracking. Using different thresholds for local vs CI accommodates PRs while still maintaining quality gates, and uploading to Codecov enables historical tracking and visualization.

**Details:**

**Threshold Configuration**
The coverage threshold variable defines the minimum coverage for CI, which is more lenient than the local threshold to accommodate PRs [6a]. The full test suite execution runs all tests with coverage for comprehensive validation including all test categories [6b].

**Scope and Enforcement**
The coverage scope definition measures coverage for the app package to focus on production code and exclude test code [6c]. Threshold enforcement fails the build if coverage is below the threshold using an environment variable to enforce the quality gate [6d].

**Codecov Integration**
The Codecov upload uploads coverage to Codecov to enable historical tracking and provide visualization [6e]. The coverage artifact specifies the XML report file used by Codecov in a machine-readable format [6f]. This enables tracking coverage trends over time and identifying regressions.

## Trace ID: 7
**Title:** Runtime Entrypoint Contract Validation

**Description:** Tests ensuring FastAPI app imports correctly and exposes required operational routes

**Motivation:**
EduBoost V2 uses runtime contract tests to ensure the FastAPI app imports correctly and exposes required operational routes for deployment and monitoring. The _load_app function loads the FastAPI app from a uvicorn-style module:attribute spec, using dynamic import to validate that the production entrypoint can be imported without errors. The test_canonical_v2_app_import_contract validates that the app has the expected title and configuration. The test_v2_runtime_exposes_required_routes verifies that operational routes (/health, /ready, /metrics) exist, as these are required for deployment orchestration and monitoring. A separate CI workflow (runtime-contract.yml) runs these tests to catch import failures early before deployment. This system ensures that the application can be deployed and monitored correctly.

**Details:**
- **Execution Flow:** Test Execution (tests/test_entrypoints.py) → _load_app(spec) function → Parse module:attribute spec → import_module(module_path) → getattr(module, attribute) → Return FastAPI instance → test_canonical_v2_app_import_contract() → app = _load_app("app.api_v2:app") → Assert app.title, docs_url, etc. → test_v2_runtime_exposes_required_routes() → route_paths = {route.path...} → assert {/health, /ready...} → CI Workflow (.github/workflows/runtime-contract.yml) → Setup Python & dependencies → pytest -c pytest.ini → Runs entrypoint tests above
- **Concurrency Safety:** Dynamic imports are thread-safe. App loading is stateless. Route extraction is deterministic. No distributed locks needed. Tests can run in parallel
- **Covered Objects:** Dynamic module import, FastAPI app loading, route extraction, operational routes validation, CI workflow, deployment contracts, monitoring endpoints
- **Timeouts:** Module import: ~10-100ms. App loading: ~10-50ms. Route extraction: ~1-5ms. Validation: ~1-5ms. Total per test: ~20-160ms
- **Migration Path:** From manual deployment checks to contract tests. Migration requires: 1) Create _load_app function, 2) Write import contract test, 3) Write route validation test, 4) Create CI workflow, 5) Enable on PR/push
- **Error Handling:** Import failures fail tests with clear message. App loading failures fail tests. Missing routes fail tests. All errors reported with module and attribute details
- **Security Considerations:** Dynamic imports should be from trusted sources. Route validation should not expose sensitive routes. Test environment should be isolated. No production credentials in tests

**Trace text diagram:**
```
Runtime Entrypoint Contract Validation
├── Test Execution (tests/test_entrypoints.py)
│   ├── _load_app(spec) function <-- 7a
│   │   ├── Parse module:attribute spec <-- test_entrypoints.py:28
│   │   ├── import_module(module_path) <-- 7b
│   │   ├── getattr(module, attribute) <-- test_entrypoints.py:32
│   │   └── Return FastAPI instance <-- test_entrypoints.py:35
│   │
│   ├── test_canonical_v2_app_import_contract() <-- test_entrypoints.py:39
│   │   ├── app = _load_app("app.api_v2:app") <-- 7c
│   │   └── Assert app.title, docs_url, etc. <-- test_entrypoints.py:43
│   │
│   └── test_v2_runtime_exposes_required_routes() <-- test_entrypoints.py:50
│       ├── route_paths = {route.path...} <-- 7d
│       └── assert {/health, /ready...} <-- 7e
│
└── CI Workflow (.github/workflows/runtime-contract.yml)
    ├── Setup Python & dependencies <-- runtime-contract.yml:44
    └── pytest -c pytest.ini <-- 7f
        └── Runs entrypoint tests above
```

**Location ID: 7a**
- **Title:** App loader function
- **Description:** Loads FastAPI app from uvicorn-style module:attribute spec
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/test_entrypoints.py:26

**Location ID: 7b**
- **Title:** Dynamic module import
- **Description:** Imports app module using importlib for runtime validation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/test_entrypoints.py:31

**Location ID: 7c**
- **Title:** Canonical app import
- **Description:** Loads production entrypoint to verify it imports without errors
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/test_entrypoints.py:41

**Location ID: 7d**
- **Title:** Route extraction
- **Description:** Collects all registered route paths from FastAPI app
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/test_entrypoints.py:53

**Location ID: 7e**
- **Title:** Operational routes validation
- **Description:** Verifies health, ready, metrics endpoints exist for deployment
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/test_entrypoints.py:55

**Location ID: 7f**
- **Title:** Runtime contract CI execution
- **Description:** Runs entrypoint tests in CI to catch import failures early
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/runtime-contract.yml:70

### AI Guide: Runtime Entrypoint Contract Validation

**Motivation:**
Runtime contract tests ensure the FastAPI app imports correctly and exposes required operational routes. Validating the production entrypoint and operational routes before deployment catches import failures early and ensures monitoring endpoints are available.

**Details:**

**App Loading**
The app loader function loads the app from a module:attribute spec using dynamic import to validate uvicorn-style specs [7a]. Dynamic module import imports the module using importlib to load at runtime and validate importability [7b]. The canonical app import loads the production entrypoint to verify the app imports without errors and validates configuration [7c].

**Route Validation**
Route extraction collects registered route paths by extracting from app.routes to validate route registration [7d]. Operational routes validation verifies that health/ready/metrics routes exist, which are required for deployment and enable monitoring [7e].

**CI Execution**
The runtime contract CI execution runs these tests in the CI workflow to catch import failures early and validate before deployment [7f]. This ensures that the application can be imported and started correctly before being deployed to production.

**Deployment Requirements:**
- Health endpoint for health checks
- Ready endpoint for readiness probes
- Metrics endpoint for monitoring
- Correct entrypoint specification
- Valid app configuration
- No import errors
