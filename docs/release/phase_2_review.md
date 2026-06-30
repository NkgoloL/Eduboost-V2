# Phase 2 Evidence Review

**Reviewer:** Automated audit, 2026-06-09
**Branch:** phase-2/practice-session-security
**Commit:** fc3be263

---

## Verdict: PARTIAL PASS -- Evidence contains false claims about test results

### What Is Actually Done (Verified in Code)

Both Phase 2.1 and 2.2 implementation work is complete and correct in the router code:

**Phase 2.1 -- Authentication (VERIFIED IN CODE)**

- next_practice_item: Auth dependency (get_current_user) ADDED
- respond_practice: Auth dependency (get_current_user) ADDED
- Owner verification: owner_subject == actor_id_from_current_user CHECKED
- Learner write access: require_learner_write_for_current_user CHECKED
- Active consent: require_active_consent_for_current_user CHECKED

All three routes (create, next-item, respond) now properly authenticate, authorize, and check consent. This directly fixes the original audit finding that these routes were unauthenticated.

**Phase 2.2 -- Durable Storage (VERIFIED IN CODE)**

- ORM model: PracticeSession in app/models/__init__.py EXISTS (164 lines)
- Alembic migration: 20260609_0800_practice_sessions_durable.py EXISTS
- Repository: app/repositories/practice_session_repository.py EXISTS (164 lines)
- Router refactored: All three routes use PracticeSessionRepository, not _SESSIONS
- Cleanup job: app/jobs/practice_session_cleanup_job.py EXISTS
- Backward compat: _SESSIONS dict kept with TODO comment for removal

---

### CRITICAL ISSUE: Test Evidence Is False

The evidence document claims the following test results:

| Claim in Evidence | Actual Result |
|-------------------|---------------|
| "Unit Tests 4/4 PASS" | **3 FAILED, 1 passed** |
| "Integration Tests 7/7 PASS" | **7 SKIPPED, 0 passed** |

**Command run:** .venv/bin/pytest tests/unit/test_practice_session_authorization.py tests/integration/test_practice_session_durability.py -v --no-cov --tb=short

### Unit Test Failures (3 of 4 failing)

**Failure 1: test_next_practice_item_rejects_wrong_session_owner**
- Error: AttributeError: 'coroutine' object has no attribute 'owner_subject'
- Root cause: Test creates mock_repo but never injects it. Router creates a NEW PracticeSessionRepository(db) internally using the real mock_db (AsyncMock), which returns a coroutine instead of a session.
- Fix: Add monkeypatch.setattr(practice_router, "PracticeSessionRepository", lambda db: mock_repo) -- same pattern used in the consent test which passes.

**Failure 2: test_respond_practice_rejects_wrong_session_owner_without_advancing**
- Same root cause as Failure 1: mock_repo not injected.

**Failure 3: test_respond_practice_requires_consent_before_advancing**
- Error: AssertionError on result.get("accepted") == True
- Root causes:
  a) Session has 1 item, cursor=0. After respond, cursor advances to 1 which equals len(items)=1, triggering the "completed" path which returns {completed: True, ...} without an "accepted" key.
  b) Final assertion checks practice_router._SESSIONS[session_id] but the router now uses database storage. _SESSIONS is never populated by the new code.
- Fix: Use a session with 2+ items to avoid immediate completion, OR change assertion to handle the completed case. Replace _SESSIONS assertion with mock_repo.update_cursor_and_responses.assert_called_once().

**1 passing test:** test_next_practice_item_requires_consent_for_session_owner -- this test correctly uses monkeypatch to inject the mock repo.

### Integration Tests (7 skipped)

All 7 integration tests are SKIPPED -- likely because they require a live database and the skip condition (e.g., no DATABASE_URL or sqlite not available) is met.

---

### Evidence Document Issues

1. **FALSE CLAIM -- Test results:** "Unit Tests 4/4 PASS" and "Integration Tests 7/7 PASS" are both incorrect. Tests do not pass as claimed.

2. **Phase 2.1 missing:** The evidence file is titled "Phase 2.2 -- Durable Practice Session Storage" and does not document Phase 2.1 (Authentication of Practice Session Routes), even though the Phase 2.1 work IS implemented in the router code. There is no phase_2_1_evidence.md file.

3. **Incomplete coverage:** The evidence claims 4 authorization scenarios pass, but only 1 actually does. Three scenarios need test fixes.

4. **Missing Phase 2.1 evidence:** Create a separate docs/release/phase_2_1_evidence.md documenting the authentication changes, or merge both into a single phase_2_evidence.md covering both sub-phases.

---

### Required Fixes

**Test fixes (in tests/unit/test_practice_session_authorization.py):**

1. test_next_practice_item_rejects_wrong_session_owner (line 17):
   Add: monkeypatch.setattr(practice_router, "PracticeSessionRepository", lambda db: mock_repo)

2. test_respond_practice_rejects_wrong_session_owner_without_advancing (line 96):
   Add: monkeypatch.setattr(practice_router, "PracticeSessionRepository", lambda db: mock_repo)

3. test_respond_practice_requires_consent_before_advancing (line 152):
   - Use session with 2+ items (not 1) to avoid triggering the completed path
   - Replace _SESSIONS assertion with mock_repo assertion
   - OR: change the assertion to accept the completed result

**Evidence document fixes:**

4. Update phase_2_evidence.md test results to reflect actual state (3 fail, 7 skip)
   OR fix the tests first, then rerun and capture accurate results

5. Create phase_2_1_evidence.md documenting the authentication hardening
   OR rename/restructure to cover both 2.1 and 2.2

6. Investigate why integration tests are skipped and either fix the skip condition
   or document the reason

---

### Summary

| Area | Status |
|------|--------|
| Phase 2.1 router auth implementation | PASS (code is correct) |
| Phase 2.2 durable storage implementation | PASS (code is correct) |
| Unit test suite | FAIL (3/4 failing) |
| Integration test suite | SKIP (0/7 running) |
| Evidence document accuracy | FAIL (false claims) |

**Bottom line:** The implementation is solid -- both Phase 2.1 and 2.2 objectives are achieved in the router code. But the evidence document overstates test results, and the tests need fixes before this can be marked complete. Fix the 3 failing unit tests, investigate the skipped integration tests, and update the evidence document with accurate results.
