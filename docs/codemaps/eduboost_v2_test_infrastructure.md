# EduBoost V2 Test Infrastructure

Multi-layered test suite covering unit tests (540+), integration tests (50+), E2E tests (16), and CI gates with pytest configuration, database fixtures, and Playwright setup. Key entry points: pytest configuration [1a], database setup [1c], integration test execution [2c], API security testing [4b], and E2E browser automation [5c].

## Trace ID: 1
**Title:** Pytest Configuration & Test Database Lifecycle

**Description:** Core test infrastructure setup - pytest markers, coverage requirements, and session-scoped database fixture creation

**Trace text diagram:**
```
Pytest Test Execution Flow
├── pytest.ini configuration
│   ├── asyncio_mode = auto <-- 1a
│   ├── testpaths = tests <-- pytest.ini:11
│   ├── markers definition (unit, integration) <-- pytest.ini:28
│   └── coverage requirements
│       └── --cov-fail-under=80 <-- 1b
│
├── tests/conftest.py (session setup)
│   ├── ensure_repo_root_on_path() <-- conftest.py:21
│   ├── set environment: APP_ENV = "test" <-- conftest.py:22
│   └── @pytest_asyncio.fixture(scope="session") <-- conftest.py:32
│       └── async test_db_setup() <-- conftest.py:33
│           ├── await drop_all_tables() <-- 1c
│           ├── await create_all_tables() <-- 1d
│           ├── yield (tests run here) <-- conftest.py:52
│           └── await drop_all_tables() (cleanup) <-- conftest.py:54
│
└── @pytest_asyncio.fixture (per-test) <-- conftest.py:57
    └── async db_session() <-- conftest.py:58
        ├── AsyncSessionFactory() as session <-- 1e
        ├── yield session (test executes) <-- conftest.py:61
        ├── await session.rollback() <-- conftest.py:65
        └── await session.close() <-- conftest.py:66
```

**Location ID: 1a**
**Title:** Pytest asyncio configuration
**Description:** Enables automatic async test detection for FastAPI/async services
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:10

**Location ID: 1b**
**Title:** Coverage threshold enforcement
**Description:** Requires 80% code coverage for CI to pass
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/pytest.ini:25

**Location ID: 1c**
**Title:** Test database cleanup
**Description:** Session-scoped fixture drops all tables before test run
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/conftest.py:44

**Location ID: 1d**
**Title:** Test schema creation
**Description:** Creates fresh database schema for test isolation
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/conftest.py:45

**Location ID: 1e**
**Title:** Test session factory
**Description:** Provides async database session to each test function
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/conftest.py:60

### AI Guide: Pytest Configuration and Test Database Lifecycle

**Motivation:**
The pytest configuration and test database lifecycle establish the foundation for reliable test execution. Asyncio mode enables automatic async test detection for FastAPI endpoints. Session-scoped database fixtures ensure test isolation by creating fresh schemas for each test run. Per-test database sessions with automatic rollback prevent test interference. Coverage thresholds enforce quality gates in CI pipelines. This infrastructure supports the full test suite from unit to E2E tests with consistent database state.

**Details:**

**Pytest Configuration**
pytest.ini configures asyncio_mode=auto for automatic async test detection [1a]. This enables testing FastAPI endpoints without manual asyncio decorators. Testpaths points to the tests directory for test discovery. Markers define test categories (unit, integration, integration, smoke) for selective test execution. Coverage requirements enforce --cov-fail-under=80 to ensure minimum code coverage [1b].

**Session-Scoped Database Setup**
The test_db_setup fixture runs once per test session [1c, 1d]. It drops all tables, creates fresh schema, and yields for test execution. This ensures complete test isolation between sessions. The fixture handles cleanup by dropping tables after tests complete. Environment APP_ENV="test" configures test-specific settings.

**Per-Test Database Sessions**
The db_session fixture provides fresh async sessions for each test [1e]. Sessions are created from AsyncSessionFactory, yielded for test execution, then rolled back and closed. Rollback ensures any database changes during tests don't affect subsequent tests. This pattern enables clean test state without expensive schema recreation.

## Trace ID: 2
**Title:** Integration Test Execution with Real Database

**Description:** Integration test flow using real PostgreSQL and fake Redis - demonstrates full service layer testing with database transactions

**Trace text diagram:**
```
Integration Test Execution Flow
├── Test Module Setup
│   ├── pytestmark = integration <-- 2a
│   └── conftest.py fixtures
│       └── monkeypatch Redis <-- 2b
├── Test Function Execution
│   ├── DiagnosticSessionService instantiation <-- test_diagnostic_session.py:18
│   ├── service.start_session() <-- 2c
│   │   └── writes to fake Redis
│   ├── service.recover_session() <-- 2d
│   │   └── reads from fake Redis
│   └── service.submit_response() <-- 2e
│       ├── IRT engine calculation
│       ├── updates ability estimate
│       └── persists to PostgreSQL
└── Test Teardown
    └── session rollback (from conftest) <-- conftest.py:65
```

**Location ID: 2a**
**Title:** Integration marker application
**Description:** Marks all tests in integration/ directory with integration marker
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/conftest.py:5

**Location ID: 2b**
**Title:** Redis dependency patching
**Description:** Replaces real Redis with in-memory fake for integration tests
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/conftest.py:95

**Location ID: 2c**
**Title:** Service method invocation
**Description:** Calls real service with real database connection
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/test_diagnostic_session.py:19

**Location ID: 2d**
**Title:** Session recovery from Redis
**Description:** Tests state persistence and recovery using fake Redis
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/test_diagnostic_session.py:21

**Location ID: 2e**
**Title:** IRT response submission
**Description:** Submits learner response and updates ability estimate
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/integration/test_diagnostic_session.py:23

### AI Guide: Integration Test Execution with Real Database

**Motivation:**
Integration tests validate service layer behavior with real database connections and external dependencies. The pytestmark=integration ensures these tests are categorized correctly. Fake Redis provides in-memory caching without external services. Real PostgreSQL connections test actual database interactions. Service layer testing validates IRT calculations, session persistence, and ability estimate updates. This approach catches integration issues that unit tests might miss.

**Details:**

**Integration Test Setup**
Integration tests use pytestmark=integration for proper categorization [2a]. The conftest.py patches Redis dependencies with fake in-memory implementations [2b]. This removes external service dependencies while maintaining caching behavior. Test database sessions provide real PostgreSQL connections for authentic integration testing.

**Service Layer Testing**
DiagnosticSessionService is instantiated with real database connections [2c]. The service.start_session() method writes session state to fake Redis. Service.recover_session() reads from Redis to test state persistence [2d]. Service.submit_response() triggers IRT engine calculations and persists ability estimates to PostgreSQL [2e]. This validates the complete diagnostic workflow.

**Test Isolation**
Each test runs with a fresh database session that's rolled back after execution. This ensures test isolation while using real database connections. Fake Redis provides clean state for each test. The combination enables realistic integration testing without external dependencies.

## Trace ID: 3
**Title:** Unit Test Service Contract Validation

**Description:** Unit test pattern for validating domain logic and state transitions without external dependencies

**Trace text diagram:**
```
Consent Lifecycle Unit Test Flow
├── Test Setup
│   └── _pending_record() factory <-- test_consent_lifecycle.py:22
│       └── Creates ConsentRecord(PENDING) <-- test_consent_lifecycle.py:23
├── State Transition Tests
│   ├── PENDING → GRANTED
│   │   ├── .grant("v1.0") call <-- 3a
│   │   └── assert state == GRANTED <-- 3b
│   ├── GRANTED → WITHDRAWN
│   │   ├── _granted_record() factory <-- test_consent_lifecycle.py:30
│   │   ├── .withdraw() call <-- 3c
│   │   └── assert state == WITHDRAWN <-- test_consent_lifecycle.py:62
│   └── Invalid Transition Guard
│       ├── _pending_record() <-- test_consent_lifecycle.py:22
│       └── pytest.raises(ValueError) <-- 3d
│           └── .withdraw() on PENDING <-- test_consent_lifecycle.py:82
└── Domain Model (ConsentRecord) <-- test_consent_lifecycle.py:14
    ├── ConsentState enum <-- test_consent_lifecycle.py:14
    └── State machine methods
        ├── grant()
        ├── withdraw()
        ├── deny()
        └── renew()
```

**Location ID: 3a**
**Title:** State transition invocation
**Description:** Tests consent state machine transition from PENDING to GRANTED
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/test_consent_lifecycle.py:44

**Location ID: 3b**
**Title:** State assertion
**Description:** Validates state transition completed correctly
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/test_consent_lifecycle.py:45

**Location ID: 3c**
**Title:** Withdrawal transition
**Description:** Tests GRANTED to WITHDRAWN state transition
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/test_consent_lifecycle.py:60

**Location ID: 3d**
**Title:** Invalid transition guard
**Description:** Ensures invalid state transitions raise exceptions
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/test_consent_lifecycle.py:81

### AI Guide: Unit Test Service Contract Validation

**Motivation:**
Unit tests validate domain logic and state transitions without external dependencies. Factory methods create test instances in specific states. State transition tests verify the consent state machine behavior. Exception testing ensures invalid transitions are properly guarded. This pattern provides fast, isolated testing of business logic with clear contract validation.

**Details:**

**Factory Method Pattern**
The _pending_record() factory creates ConsentRecord instances in PENDING state [3a]. The _granted_record() factory creates instances in GRANTED state. Factories encapsulate test setup complexity and ensure consistent test data creation across multiple test cases.

**State Transition Testing**
Tests verify valid state transitions: PENDING → GRANTED via .grant("v1.0") [3a, 3b]. GRANTED → WITHDRAWN via .withdraw() [3c]. Each transition validates the resulting state and any side effects (timestamps, audit trails). This ensures the state machine behaves as specified.

**Guard Clause Testing**
pytest.raises(ValueError) validates that invalid transitions raise exceptions [3d]. Attempting .withdraw() on PENDING state should fail. This tests the defensive programming aspects of the state machine. Guard clause testing prevents invalid state changes that could corrupt data integrity.

## Trace ID: 4
**Title:** API Route Security Testing with TestClient

**Description:** API test pattern using FastAPI TestClient with dependency overrides to validate authentication and authorization

**Trace text diagram:**
```
API Route Security Testing Flow
├── Test Setup Phase
│   ├── FastAPI app initialization <-- test_learner_content_routes.py:10
│   ├── Dependency override configuration <-- 4a
│   │   └── Mock user injection (_learner_user) <-- test_learner_content_routes.py:38
│   └── TestClient instantiation <-- test_learner_content_routes.py:62
├── Unauthenticated Request Test
│   ├── Clear dependency overrides <-- test_learner_content_routes.py:75
│   ├── GET /api/v2/learner/content/... <-- 4b
│   └── Assert status == 401 <-- 4c
└── Router Security Validation
    ├── Import content_factory router <-- test_content_factory_route_security.py:44
    ├── Extract router.dependencies <-- test_content_factory_route_security.py:48
    └── Assert require_admin present <-- 4d
```

**Location ID: 4a**
**Title:** Dependency override setup
**Description:** Replaces auth dependency with mock user for testing
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/api/test_learner_content_routes.py:59

**Location ID: 4b**
**Title:** Unauthenticated request
**Description:** Tests route without authentication after clearing overrides
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/api/test_learner_content_routes.py:76

**Location ID: 4c**
**Title:** Authorization failure assertion
**Description:** Verifies unauthenticated requests are rejected
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/api/test_learner_content_routes.py:77

**Location ID: 4d**
**Title:** Router-level security check
**Description:** Validates admin-only routes have require_admin dependency
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/test_content_factory_route_security.py:48

### AI Guide: API Route Security Testing

**Motivation:**
API route security testing validates authentication and authorization controls. FastAPI TestClient enables HTTP endpoint testing without a running server. Dependency overrides replace authentication with mock users for controlled testing. Unauthenticated request tests ensure routes are properly protected. Router-level security checks validate dependency injection of security middleware. This pattern prevents security regressions in API endpoints.

**Details:**

**Dependency Override Pattern**
TestClient is created with FastAPI app instance [4a]. Dependency overrides replace get_current_user with _learner_user mock [4a]. This enables testing protected routes without real authentication. Overrides are cleared before unauthenticated tests to ensure proper security validation.

**Unauthenticated Request Testing**
After clearing dependency overrides, GET requests to protected routes should return 401 [4b, 4c]. This validates that routes are properly protected when no authentication is provided. The test ensures security middleware is functioning correctly.

**Router-Level Security Validation**
Tests extract router.dependencies to verify require_admin is present on admin-only routes [4d]. This validates that security dependencies are properly declared at the router level. The pattern catches missing security dependencies that could expose protected endpoints.

## Trace ID: 5
**Title:** E2E Playwright Test Execution Flow

**Description:** Browser-based E2E testing with Playwright using mocked API routes for isolated frontend testing

**Trace text diagram:**
```
E2E Playwright Test: Password Reset Flow
├── Test Setup
│   └── mockForgotPassword() helper <-- auth.spec.ts:23
│       └── page.route() intercepts API <-- 5a
├── Test Execution
│   ├── Navigation
│   │   └── page.goto("/auth/reset-password") <-- 5b
│   ├── User Interaction
│   │   ├── getByTestId("email-input").fill() <-- 5c
│   │   └── getByTestId("submit-btn").click() <-- 5d
│   └── Assertion
│       └── expect(sent-message).toBeVisible() <-- 5e
└── Playwright Test Runner
    └── Browser automation engine
        └── Frontend renders success state
```

**Location ID: 5a**
**Title:** API route interception
**Description:** Mocks backend API calls for isolated frontend testing
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/e2e/auth.spec.ts:24

**Location ID: 5b**
**Title:** Page navigation
**Description:** Navigates to password reset page in browser
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/e2e/auth.spec.ts:87

**Location ID: 5c**
**Title:** User interaction simulation
**Description:** Simulates user filling form input field
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/e2e/auth.spec.ts:97

**Location ID: 5d**
**Title:** Form submission
**Description:** Simulates user clicking submit button
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/e2e/auth.spec.ts:98

**Location ID: 5e**
**Title:** UI state assertion
**Description:** Verifies success message appears after submission
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/e2e/auth.spec.ts:100

### AI Guide: E2E Playwright Test Execution

**Motivation:**
E2E tests validate complete user workflows through the browser interface. Playwright provides browser automation for realistic user interaction testing. API route mocking isolates frontend testing from backend dependencies. Test data attributes (data-testid) enable reliable element selection. This pattern catches integration issues between frontend and backend that unit tests might miss.

**Details:**

**API Route Mocking**
mockForgotPassword() helper intercepts API calls using page.route() [5a]. The mock returns predefined responses, eliminating backend dependencies. This enables isolated frontend testing with predictable data. Mocking also speeds up test execution by removing network latency.

**Browser Automation**
page.goto() navigates to the password reset page [5b]. getByTestId() locates elements using test-specific attributes for reliable selection. fill() and click() simulate user interactions [5c, 5d]. Playwright's auto-waiting ensures elements are ready before interaction.

**UI State Validation**
expect().toBeVisible() validates UI state changes [5e]. Success message visibility confirms the workflow completed correctly. These assertions verify that the frontend properly handles API responses and updates the UI accordingly.

## Trace ID: 6
**Title:** CI Item Bank Coverage Gate Validation

**Description:** CI-specific test that queries production database to enforce minimum item counts per CAPS reference

**Trace text diagram:**
```
CI Item Bank Coverage Gate (Trace 6)
├── Test Module Entry
│   ├── pytest.mark.skipif conditional <-- 6a
│   └── EDUBOOST_RUN_ITEM_BANK_CI=1 check <-- test_item_bank_coverage.py:19
├── Database Connection Setup
│   ├── @pytest.fixture(scope="module") <-- test_item_bank_coverage.py:43
│   └── asyncpg.create_pool() <-- 6b
├── Test Execution (per CAPS ref)
│   ├── @pytest.mark.parametrize("caps_ref", ...) <-- test_item_bank_coverage.py:120
│   ├── test_approved_item_count_meets_minimum() <-- test_item_bank_coverage.py:121
│   │   ├── count_approved_items() call <-- 6c
│   │   │   └── SELECT COUNT(*) query <-- test_item_bank_coverage.py:65
│   │   └── assert count >= MIN_APPROVED <-- 6d
│   └── Additional validation tests
│       ├── test_approved_items_have_valid... <-- test_item_bank_coverage.py:141
│       └── test_difficulty_distribution... <-- test_item_bank_coverage.py:173
└── CI Build Gate
    └── Fail build if assertion fails <-- test_item_bank_coverage.py:132
```

**Location ID: 6a**
**Title:** CI gate conditional execution
**Description:** Only runs when EDUBOOST_RUN_ITEM_BANK_CI=1 is set
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/ci/test_item_bank_coverage.py:18

**Location ID: 6b**
**Title:** Database connection pool
**Description:** Creates direct asyncpg connection to production database
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/ci/test_item_bank_coverage.py:54

**Location ID: 6c**
**Title:** Coverage query execution
**Description:** Queries approved item count for specific CAPS reference
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/ci/test_item_bank_coverage.py:130

**Location ID: 6d**
**Title:** Coverage threshold enforcement
**Description:** Fails CI build if item count below minimum threshold
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/ci/test_item_bank_coverage.py:131

### AI Guide: CI Item Bank Coverage Gate Validation

**Motivation:**
CI item bank coverage tests enforce minimum content requirements before deployment. These tests query the production database to validate item counts per CAPS reference. Skipif condition ensures tests only run in CI environments with proper database access. Parametrized testing validates each CAPS reference individually. Coverage thresholds prevent deployment with insufficient content, ensuring curriculum coverage.

**Details:**

**Conditional Test Execution**
pytest.mark.skipif ensures tests only run when EDUBOOST_RUN_ITEM_BANK_CI=1 is set [6a]. This prevents tests from running in development without database access. The conditional enables CI-specific validation without affecting local development workflows.

**Database Connection**
asyncpg.create_pool() creates direct database connections for efficient querying [6b]. Module-scoped fixture reuses connection across tests. Direct SQL queries provide precise control over coverage validation without ORM overhead.

**Coverage Validation**
Parametrized tests run for each CAPS reference [6c]. count_approved_items() queries approved item counts with SELECT COUNT(*) [6c]. Assertions enforce MIN_APPROVED thresholds per reference [6d]. Additional tests validate item quality and difficulty distribution. Failed assertions block deployment, ensuring adequate content coverage.

## Trace ID: 7
**Title:** Health Check Testing with Mocked Dependencies

**Description:** Testing pattern for health check endpoints using AsyncMock to simulate dependency states

**Trace text diagram:**
```
Health Check Testing Flow
├── Test Setup
│   └── patch() health check functions <-- 7a
│       └── mock_secrets.return_value = ok <-- 7b
├── Happy Path Test
│   ├── client.get("/ready") <-- 7c
│   │   └── app.core.health module <-- test_health_checks.py:7
│   │       ├── check_required_secrets() [mocked] <-- test_health_checks.py:8
│   │       ├── check_postgres() [mocked] <-- test_health_checks.py:9
│   │       ├── check_redis() [mocked] <-- test_health_checks.py:10
│   │       └── gather_deep_health() <-- test_health_checks.py:13
│   └── assert status_code == 200 <-- 7d
└── Failure Path Test
    ├── mock_secrets.return_value = error <-- 7e
    ├── client.get("/ready") <-- test_health_checks.py:88
    │   └── gather_deep_health() <-- test_health_checks.py:13
    │       └── detects critical failure
    └── assert status_code == 503 <-- 7f
```

**Location ID: 7a**
**Title:** Health check mocking setup
**Description:** Patches all health check functions with AsyncMock
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/test_health_checks.py:43

**Location ID: 7b**
**Title:** Mock return value configuration
**Description:** Configures mock to return healthy status
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/test_health_checks.py:51

**Location ID: 7c**
**Title:** Readiness endpoint invocation
**Description:** Calls /ready endpoint with mocked dependencies
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/test_health_checks.py:60

**Location ID: 7d**
**Title:** Health status assertion
**Description:** Verifies endpoint returns 200 when all checks pass
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/test_health_checks.py:62

**Location ID: 7e**
**Title:** Failure scenario simulation
**Description:** Configures mock to simulate missing secrets error
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/test_health_checks.py:79

**Location ID: 7f**
**Title:** Degraded state assertion
**Description:** Verifies endpoint returns 503 when critical check fails
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/test_health_checks.py:90

### AI Guide: Health Check Testing with Mocked Dependencies

**Motivation:**
Health check testing validates application readiness and dependency monitoring. AsyncMock patches simulate different dependency states without requiring actual services. Happy path tests verify 200 responses when all dependencies are healthy. Failure path tests validate 503 responses for critical failures. This pattern ensures health check endpoints accurately reflect application state for orchestration systems.

**Details:**

**Mock Configuration**
patch() replaces health check functions with AsyncMock instances [7a]. Mock return values are configured to simulate healthy (ok) or error states [7b]. This enables testing different scenarios without actual dependencies. Multiple patches ensure all health checks are controlled.

**Happy Path Testing**
client.get("/ready") invokes the readiness endpoint with mocked healthy dependencies [7c]. The gather_deep_health() function aggregates check results. Assertions verify 200 status code when all checks pass [7d]. This validates the endpoint correctly reports healthy state.

**Failure Path Testing**
Mock configuration simulates missing secrets error [7e]. The readiness endpoint should detect critical failures and return 503 status [7f]. This validates proper error handling and status reporting. Different failure scenarios can be tested by configuring various mock return values.

## Trace ID: 8
**Title:** Smoke Test Runtime Validation

**Description:** Lightweight smoke tests that verify basic API functionality without full database setup

**Trace text diagram:**
```
Smoke Test Runtime Validation (Trace 8)
├── Test Module Setup
│   └── TestClient initialization <-- 8a
│       └── FastAPI app instance <-- test_v2_smoke.py:11
│           └── raise_server_exceptions=False <-- test_v2_smoke.py:13
├── Health Endpoint Tests
│   └── GET /health request <-- 8b
│       └── Assert status == 200 <-- test_v2_smoke.py:19
│           └── Assert response has version <-- test_v2_smoke.py:22
├── Authentication Tests
│   ├── GET /v2/auth/me (no auth) <-- 8c
│   │   └── Assert status == 401 <-- test_v2_smoke.py:65
│   └── GET /v2/auth/me (invalid token) <-- test_v2_smoke.py:68
│       └── Assert status == 401 <-- test_v2_smoke.py:69
└── OpenAPI Schema Tests
    └── GET /openapi.json <-- 8d
        └── Assert status == 200 <-- test_v2_smoke.py:120
            └── Assert schema has paths <-- test_v2_smoke.py:123
```

**Location ID: 8a**
**Title:** Test client initialization
**Description:** Creates FastAPI test client with exception suppression
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/smoke/test_v2_smoke.py:13

**Location ID: 8b**
**Title:** Health endpoint smoke test
**Description:** Verifies basic health endpoint responds
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/smoke/test_v2_smoke.py:18

**Location ID: 8c**
**Title:** Protected endpoint test
**Description:** Verifies protected routes require authentication
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/smoke/test_v2_smoke.py:64

**Location ID: 8d**
**Title:** OpenAPI schema validation
**Description:** Ensures API schema is accessible and valid
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/smoke/test_v2_smoke.py:119

### AI Guide: Smoke Test Runtime Validation

**Motivation:**
Smoke tests provide lightweight validation of basic API functionality without full database setup. TestClient with suppressed exceptions enables quick endpoint testing. Health endpoint tests verify application startup. Authentication tests validate security middleware. OpenAPI schema tests ensure API documentation is accessible. These tests catch basic configuration issues before running full test suites.

**Details:**

**Test Client Setup**
TestClient is created with FastAPI app instance and raise_server_exceptions=False [8a]. This prevents exceptions from stopping test execution, allowing assertion-based testing. The configuration enables quick smoke testing without full dependency setup.

**Basic Endpoint Validation**
GET /health tests verify the application starts and responds [8b]. Assertions check for 200 status and version information. Authentication tests verify protected routes return 401 without credentials [8c]. This validates security middleware is properly configured.

**API Documentation Tests**
GET /openapi.json tests verify API documentation is accessible [8d]. Assertions check for 200 status and presence of paths in the schema. This ensures API documentation generation is working correctly for developer tools.
