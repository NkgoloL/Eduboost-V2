# Code Coverage Improvement Handover

**Objective**: Increase overall code coverage from ~65% to 70%, with 90% target for `app/core/` directory (Task T132).

**Branch**: `remediation/phase0-phase1`

**Date**: June 1, 2026

---

## Current Status

### Overall Coverage
- **Current**: 66.45% (up from 66.41%)
- **Target**: 70% overall, 90% for `app/core/`
- **Test Results**: 2858 passed, 258 skipped

### Key Service Coverages
| Service | Coverage | Uncovered Lines | Status |
|---------|----------|-----------------|--------|
| popia_service.py | 74% | 37 lines | ✅ Improved |
| quota_service.py | 37% | 42 lines | ⚠️ Needs work |
| learner_service.py | 33% | 82 lines | ⚠️ Needs work |
| diagnostic_transactional_response.py | 33% | 50 lines | 🔄 In Progress |
| email_service.py | 56% | 54 lines | ⚠️ Needs work |
| lesson_context_builder.py | 79% | 27 lines | ✅ Good |
| job_runtime_integrity.py | 18% | 60 lines | ⚠️ Needs work |

---

## Completed Work

### 1. popia_service.py (74% coverage)
**File**: `tests/unit/test_popia_service.py`

**Tests Added**:
- Constants and dataclass tests (POPIA_EXPORT_SLA_DAYS, RightsRequestStatus)
- Helper function tests (_now, _iso, _to_csv, _status)
- Business logic tests (requires_admin_review, request_correction, restrict_processing)
- Export tests (build_learner_export JSON/CSV branches)
- Erasure tests (request_erasure, cancel_erasure, _postflight_erasure_verification)

**Commits**:
- `tests: add POPIA constants and helper tests`
- `tests: add POPIA business logic tests`
- `tests: add export and postflight tests for popia_service`
- `tests: add erasure request and cancel tests for popia_service`

### 2. quota_service.py (37% coverage)
**File**: `tests/unit/test_quota_service.py`

**Tests Added**:
- Constructor tests (QuotaService, SemanticCacheService)
- Constants tests (_QUOTA_KEY, _CACHE_KEY, QuotaExceededError)
- Edge cases (expiry logic, rollback, exact limit, error details)

**Commits**:
- `tests: add quota_service constructor and constants tests`
- `tests: add quota_service edge case tests`

### 3. Other Services
- **gamification_service_v2.py**: 100% coverage
- **job_runtime_integrity.py**: Improved to cover exception paths
- **lesson_context_builder.py**: 79% coverage
- **subscription_service.py**: 100% coverage
- **study_plan_service_v2.py**: 94% coverage
- **study_plan_updater.py**: 94% coverage

---

## In Progress

### diagnostic_transactional_response.py
**File**: `tests/unit/test_diagnostic_transactional_response.py` (newly created)

**Status**: Tests written but failing due to async context manager mocking issues.

**Problem**: The transaction rollback tests (`fail_after_response`, `fail_after_mastery`, `fail_after_audit`) are failing because the async context manager mocks don't properly simulate the transaction boundary.

**Error**: `TypeError: mock_aenter() takes 0 positional arguments but 1 was given`

**Fix Needed**: Update the async context manager mocks to accept `self` parameter:
```python
async def mock_aenter(self):
    return mock_session

async def mock_aexit(self, exc_type, exc_val, exc_tb):
    return None
```

**Tests Written**:
- Dataclass tests (DiagnosticTransactionInput, DiagnosticTransactionResult)
- Constructor tests
- Success path test (submit_response completes all three writes)
- Failure path tests (fail_after_response, fail_after_mastery, fail_after_audit) - ❌ Failing
- ID generation test
- Custom clock test

---

## Pending Work

### High Priority (Most Impact)

1. **Fix diagnostic_transactional_response.py tests**
   - Fix async context manager mocks
   - Run tests to verify they pass
   - Commit: `tests: add diagnostic_transactional_response unit tests`
   - Expected coverage gain: 33% → 80%+

2. **quota_service.py (37% → 70%)**
   - File: `tests/unit/test_quota_service.py`
   - Add tests for uncovered lines (42 lines)
   - Focus on: premium tier logic, edge cases, error handling
   - Expected coverage gain: +33%

3. **learner_service.py (33% → 70%)**
   - File: `tests/unit/test_learner_service.py`
   - Note: Coverage report shows 122 lines but file is only 12 lines - investigate discrepancy
   - May be a different learner_service.py file or coverage reporting issue
   - Expected coverage gain: +37%

### Medium Priority

4. **email_service.py (56% → 70%)**
   - File: `tests/unit/test_email_service.py`
   - Add tests for uncovered lines (54 lines)
   - Focus on: SendGrid integration, template rendering, error handling

5. **job_runtime_integrity.py (18% → 50%)**
   - File: `tests/unit/test_job_runtime_integrity.py`
   - Add tests for uncovered lines (60 lines)
   - Focus on: Runtime object detection, circular references

### Low Priority

6. **diagnostic_transactional_response.py contracts**
   - File: `tests/unit/test_diagnostic_transactional_response_contracts.py`
   - Already has contract tests, just need unit tests fixed

---

## Environment Setup

### Running Tests
```bash
# Set encryption key
export ENCRYPTION_KEY=$(python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())")

# Run targeted coverage
.venv/bin/python -m pytest tests/unit/test_<service>.py --cov=app/services/<service>.py --cov-report=term-missing -v

# Run full coverage suite
.venv/bin/python -m pytest --cov=app --cov-report=term-missing --no-cov-on-fail -q
```

### Commit Pattern
1. Write tests for specific service
2. Run targeted coverage to verify
3. Commit with descriptive message: `tests: add <service> tests for <feature>`
4. Run full coverage suite to verify overall gains
5. Proceed to next service

---

## Notes for Next Agent

1. **Test Environment**: Always set `ENCRYPTION_KEY` before running pytest
2. **Async Mocking**: When mocking async context managers, ensure the `aenter` and `aexit` methods accept the proper parameters
3. **Coverage Discrepancies**: Some files show more lines in coverage reports than actual file length - investigate before adding tests
4. **Focus on High Impact**: Prioritize services with most uncovered lines and lowest coverage percentages
5. **Module-Level Coverage**: Some services show low coverage due to module-level import patterns - check if tests actually exist but aren't being counted

---

## Git History

Recent commits on `remediation/phase0-phase1`:
```
7808dd9f tests: add erasure request and cancel tests for popia_service
<earlier commits for other services>
```

---

## Next Steps

1. Fix diagnostic_transactional_response.py test mocks
2. Commit and push current work
3. Continue with quota_service.py tests
4. Run full coverage suite after each major addition
5. Aim for 70% overall coverage before merging
