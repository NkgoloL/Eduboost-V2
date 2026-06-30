# Phase 8 Evidence - Privacy and Authorization Completion

**Evidence date:** 2026-06-14
**Status:** Supported after remediation; DB-backed rate-limit tests skipped locally because PostgreSQL was unavailable

## Evidence Sources

- `docs/roadmap/execution/phase_8_execution_plan.md`
- `docs/roadmap/execution/phase_8_implementation_report.md`
- `docs/release/phase_8_implementation_audit.md`
- `app/api_v2_routers/popia.py`
- `app/services/popia_service.py`
- `app/services/auth_service.py`
- `app/security/dependencies.py`
- Phase 8-related tests and security docs

## Remediation Performed During Audit

The 2026-06-13 audit found that POPIA data-rights service methods still expected
dict-style user claims while the active router dependency returns `AuthContext`.
That caused a real runtime mismatch before database access:

```text
AttributeError: 'AuthContext' object has no attribute 'get'
```

The 2026-06-14 remediation:

- Normalized POPIA actor and role extraction for both `AuthContext` and legacy dict claims in `app/services/popia_service.py`.
- Added `tests/unit/test_phase8_popia_auth_context.py` to exercise POPIA service behavior with an actual `AuthContext`.
- Moved the emergency revoke-all import seam in `app/services/auth_service.py` so the existing revocation tests can patch the production call reliably.
- Updated Phase 2/Phase 8 authorization evidence from the retired `ether.py` router to the active `onboarding.py` router.

## Passing Evidence

```text
python3 -m py_compile app/services/auth_service.py app/services/popia_service.py \
  scripts/check_phase2_authorization_evidence.py \
  tests/unit/test_phase8_popia_auth_context.py \
  tests/unit/test_ether_onboarding_questions_auth_boundary.py \
  tests/unit/test_check_learner_authz_coverage.py \
  tests/unit/test_ether_onboarding_consent_gate_wiring.py
# passed
```

```text
python3 scripts/check_phase2_authorization_evidence.py
# passed
```

```text
python3 -m pytest --no-cov -q \
  tests/unit/test_emergency_revocation.py \
  tests/unit/test_ether_onboarding_questions_auth_boundary.py \
  tests/unit/test_check_learner_authz_coverage.py \
  tests/unit/test_ether_onboarding_consent_gate_wiring.py \
  tests/unit/test_phase8_popia_auth_context.py \
  tests/unit/test_sprint3_popia_router_data_rights.py
# 18 passed
```

```text
python3 -m pytest --no-cov -q \
  tests/unit/test_popia_data_rights_consent_boundary.py \
  tests/unit/test_popia_correction_request_authorization_wiring.py \
  tests/unit/test_popia_restriction_request_authorization_wiring.py \
  tests/unit/test_popia_deletion_request_authorization_wiring.py \
  tests/unit/test_popia_deletion_cancel_authorization_wiring.py \
  tests/unit/test_popia_data_export_authorization_wiring.py \
  tests/unit/test_phase8_popia_auth_context.py \
  tests/unit/test_sprint3_popia_router_data_rights.py -rs
# 11 passed
```

```text
python3 -m pytest --no-cov -q \
  tests/unit/test_auth_abuse_paths.py \
  tests/unit/test_token_rotation.py \
  tests/unit/test_emergency_revocation.py \
  tests/unit/test_cookie_policy.py \
  tests/unit/test_role_authorization.py \
  tests/integration/test_auth_rate_limits.py -rs
# 65 passed, 12 skipped
# skipped tests require a local PostgreSQL test database at 127.0.0.1:5432
```

```text
python3 scripts/check_privacy_boundary_evidence.py
# passed
```

## Residual Limits

- The local run did not prove DB-backed auth rate-limit behavior because the test database was unavailable.
- The original Phase 8 execution plan contains broader aspirational PR-004 tasks than the merged PR actually delivered. The completion claim is therefore limited to the implemented authorization/privacy evidence set and the POPIA AuthContext remediation above, not every unchecked planning item in the original execution plan.

## Verdict

Phase 8 should no longer remain reopened for the POPIA `AuthContext` runtime mismatch. The corrected code and focused tests now support the implemented Phase 8 privacy/authorization scope, with the DB-backed rate-limit skip explicitly recorded.
