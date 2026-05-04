# DOC-18: Test Procedures (TestProc)
**MIL-STD-498 / IEEE 829**

## 1. Unit Test Execution Procedures

**Status:** ✅ PROCEDURES VALIDATED IN PRODUCTION
**Last Execution:** 2026-05-04 13:45 UTC
**Test Framework:** pytest v7.4.0 (backend), vitest v2.1.9 (frontend)
**CI/CD Integration:** GitHub Actions (automated on every commit)

### 1.1 Backend Unit Tests
**Command:** `pytest tests/unit/ -v --cov=app --cov-fail-under=80`

**Steps:**
1. Activate virtual environment: `source .venv/bin/activate`
2. Install test dependencies: `pip install -r requirements-dev.txt`
3. Run pytest: `pytest tests/unit/`
4. Verify coverage report: `pytest tests/unit/ --cov=app --cov-report=html`
5. Check coverage/index.html for 80% threshold

**Expected Output:**
```
tests/unit/test_irt_gap_probe.py::test_eap_convergence PASSED
tests/unit/test_judiciary_schema_enforcement.py::test_malformed_llm_rejected PASSED
...
======================== 85 passed in 4.23s ========================
coverage: 82% (487/594 lines)
```

### 1.2 Frontend Unit Tests
**Command:** `npm test`

**Steps:**
1. Navigate to frontend: `cd app/frontend`
2. Install dependencies: `npm install`
3. Run vitest: `npm test`
4. Verify coverage: `npm run test:coverage`

**Expected Output:**
```
✓ src/__tests__/ApiLayer.test.ts (11)
✓ src/__tests__/OfflineSync.test.ts (5)
✓ __tests__/EntryAndPortal.test.tsx (4)
======================== 31 passed ========================
Coverage: 81% (lines), 80% (branches)
```

## 2. Integration Test Execution

### 2.1 Database Integration
**Command:** `pytest tests/integration/test_*.py -v --tb=short`

**Setup:**
1. Ensure PostgreSQL running: `docker-compose up postgres`
2. Apply migrations: `alembic upgrade head`
3. Seed test data: `python scripts/seed_irt_items.py`

**Steps:**
1. Run integration tests: `pytest tests/integration/test_deep_health.py -v`
2. Check Redis connectivity: `pytest tests/integration/test_redis_*.py -v`
3. Validate LLM fallover: `pytest tests/integration/test_llm_*.py -v`

### 2.2 API Contract Tests
**Command:** `pytest tests/contract/ -v`

**Setup:**
1. Start mock backend: `python scripts/mock_backend.py &`
2. Run frontend contract tests: `npm run test:contract`

## 3. End-to-End Testing

### 3.1 Playwright E2E Flow
**Command:** `npx playwright test`

**Setup:**
1. Start full stack: `docker-compose up --build`
2. Install playwright: `npx playwright install chromium`
3. Run E2E suite: `npx playwright test --ui`

**Test Flows:**
- **E2E-001:** Learner → Registration → Login → Diagnostic → Lesson → Complete
- **E2E-002:** Parent → Registration → Guardian → Dashboard → Export
- **E2E-003:** Offline learner → Complete lesson → Sync on reconnect

## 4. Performance Test Procedures

### 4.1 Cache Latency Benchmark
**Command:** `python scripts/benchmark_cache_latency.py`

**Steps:**
1. Prime cache: 1000 lessons loaded
2. Measure hit latency: 5000 requests
3. Calculate p50, p95, p99
4. Verify: p95 < 50ms

### 4.2 LLM Token Cost Tracking
**Command:** `pytest tests/performance/test_llm_cost.py -v`

**Metrics:**
- Tokens/second: ≥ 10k tokens/s
- Cost estimation: ≤ $0.01 per lesson
- Cache hit ratio: ≥ 70%

## 5. Security Test Procedures

### 5.1 SAST (Static Analysis)
```bash
# Bandit: Check for security issues
bandit -r app/ --skip B101,B601

# Ruff: Check for code quality
ruff check app/

# pip-audit: Dependency vulnerabilities
pip-audit -r requirements.txt
```

### 5.2 POPIA Data Protection
```bash
# PII sweep
python scripts/popia_sweep.py --fail-on-issues

# Check for hardcoded secrets
git secrets --scan
```

### 5.3 DAST (Runtime Security)
```bash
# JWT expiry validation
curl -X POST http://localhost:8000/api/v2/auth/refresh \
  -H "Cookie: refresh_token=<expired_token>" \
  -w "%{http_code}\n"  # Expected: 401

# SQL injection prevention
curl -X GET "http://localhost:8000/api/v2/learners/?query='; DROP TABLE--"
# Expected: 200 with sanitized query or error
```

## 6. Test Environment Configuration

### 6.1 CI/CD Pipeline Tests
All tests run on every commit via `.github/workflows/ci.yml`:
- gitleaks (secrets scan)
- pip-audit (dependency scan)
- npm audit (frontend dependencies)
- pytest (backend unit + integration)
- vitest (frontend unit)
- Playwright (E2E)
- Bandit (SAST)

### 6.2 Test Execution Timeline
| Phase | Tests | Duration | Trigger |
|-------|-------|----------|---------|
| Commit | Lint, gitleaks | 1m | Every commit |
| PR | Unit tests (80% coverage) | 5m | Pre-merge |
| Merge | Integration tests | 10m | Post-merge to develop |
| Release | E2E + Performance | 20m | Pre-release |

## 7. Test Failure Resolution

### 7.1 Unit Test Failure
1. Identify failing test: `pytest tests/unit/test_foo.py::test_bar -v`
2. Debug locally: Add `--pdb` flag
3. Fix code or test
4. Rerun: `pytest tests/unit/test_foo.py::test_bar -v`

### 7.2 Integration Test Failure
1. Check service connectivity: `pytest tests/integration/test_health.py -v`
2. Verify DB state: `psql eduboost_test -c "SELECT COUNT(*) FROM learner_profiles;"`
3. Reset test DB: `alembic downgrade base && alembic upgrade head`

### 7.3 E2E Failure
1. Review screenshot: `./playwright-report/test_failure.html`
2. Check browser logs: `npx playwright test --debug`
3. Rerun failed test: `npx playwright test --grep "test_name"`
