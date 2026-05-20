# Route Transaction Implementation Plan

Generated at: `2026-05-19T23:09:25Z`
Commit: `9e706b9e0b787b0e4fb7324c9beefeb3fe35d2a4`

- Source inventory: `docs/architecture/tx_route_wiring_inventory.json`
- Source status: `production-route-transaction-wiring-not-proven`
- Plan status: `blocked-until-route-wiring-and-live-db-proof`
- Action count: `15`

## Ordered implementation actions

| Priority | ID | Domain | Route function | File | Line | Service hint | Live DB proof required |
|---|---|---|---|---|---:|---|---:|
| `P0` | `ROUTE-TX-001-auth-register` | `auth` | `register` | `app/api_v2_routers/auth.py` | 89 | `TransactionalAuthRegistrationService` | True |
| `P0` | `ROUTE-TX-002-auth-create_dev_session` | `auth` | `create_dev_session` | `app/api_v2_routers/auth.py` | 126 | `TransactionalAuthRegistrationService` | True |
| `P0` | `ROUTE-TX-003-popia-grant_consent` | `popia` | `grant_consent` | `app/api_v2_routers/popia.py` | 102 | `TransactionalPOPIAConsentLifecycleService` | True |
| `P0` | `ROUTE-TX-004-popia-deny_consent` | `popia` | `deny_consent` | `app/api_v2_routers/popia.py` | 120 | `TransactionalPOPIAConsentLifecycleService` | True |
| `P0` | `ROUTE-TX-005-popia-withdraw_consent` | `popia` | `withdraw_consent` | `app/api_v2_routers/popia.py` | 138 | `TransactionalPOPIAConsentLifecycleService` | True |
| `P0` | `ROUTE-TX-006-popia-renew_consent` | `popia` | `renew_consent` | `app/api_v2_routers/popia.py` | 153 | `TransactionalPOPIAConsentLifecycleService` | True |
| `P0` | `ROUTE-TX-007-popia-create_export_request` | `popia` | `create_export_request` | `app/api_v2_routers/popia.py` | 173 | `TransactionalPOPIAConsentLifecycleService` | True |
| `P1` | `ROUTE-TX-008-diagnostics-submit_diagnostic` | `diagnostics` | `submit_diagnostic` | `app/api_v2_routers/diagnostics.py` | 81 | `TransactionalDiagnosticResponseService` | True |
| `P1` | `ROUTE-TX-009-diagnostics-start_diagnostic_session` | `diagnostics` | `start_diagnostic_session` | `app/api_v2_routers/diagnostics.py` | 229 | `TransactionalDiagnosticResponseService` | True |
| `P1` | `ROUTE-TX-010-diagnostics-diagnostic_respond` | `diagnostics` | `diagnostic_respond` | `app/api_v2_routers/diagnostics.py` | 293 | `TransactionalDiagnosticResponseService` | True |
| `P2` | `ROUTE-TX-011-lessons-generate_lesson` | `lessons` | `generate_lesson` | `app/api_v2_routers/lessons.py` | 33 | `TransactionalLessonCompletionService` | True |
| `P2` | `ROUTE-TX-012-lessons-generate_lesson_stream` | `lessons` | `generate_lesson_stream` | `app/api_v2_routers/lessons.py` | 58 | `TransactionalLessonCompletionService` | True |
| `P2` | `ROUTE-TX-013-lessons-get_lesson` | `lessons` | `get_lesson` | `app/api_v2_routers/lessons.py` | 81 | `TransactionalLessonCompletionService` | True |
| `P2` | `ROUTE-TX-014-lessons-complete_lesson` | `lessons` | `complete_lesson` | `app/api_v2_routers/lessons.py` | 102 | `TransactionalLessonCompletionService` | True |
| `P2` | `ROUTE-TX-015-lessons-sync_lessons` | `lessons` | `sync_lessons` | `app/api_v2_routers/lessons.py` | 119 | `TransactionalLessonCompletionService` | True |

## Implementation detail

### ROUTE-TX-001-auth-register

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/auth.py:register` to delegate mutation work to `TransactionalAuthRegistrationService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: register rollback: fail after user/guardian/learner creation and assert no partial rows remain
- Static marker closure allowed: `False`

### ROUTE-TX-002-auth-create_dev_session

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/auth.py:create_dev_session` to delegate mutation work to `TransactionalAuthRegistrationService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: register rollback: fail after user/guardian/learner creation and assert no partial rows remain
- Static marker closure allowed: `False`

### ROUTE-TX-003-popia-grant_consent

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/popia.py:grant_consent` to delegate mutation work to `TransactionalPOPIAConsentLifecycleService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: consent lifecycle rollback: fail after consent/audit write and assert atomic rollback
- Static marker closure allowed: `False`

### ROUTE-TX-004-popia-deny_consent

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/popia.py:deny_consent` to delegate mutation work to `TransactionalPOPIAConsentLifecycleService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: consent lifecycle rollback: fail after consent/audit write and assert atomic rollback
- Static marker closure allowed: `False`

### ROUTE-TX-005-popia-withdraw_consent

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/popia.py:withdraw_consent` to delegate mutation work to `TransactionalPOPIAConsentLifecycleService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: consent lifecycle rollback: fail after consent/audit write and assert atomic rollback
- Static marker closure allowed: `False`

### ROUTE-TX-006-popia-renew_consent

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/popia.py:renew_consent` to delegate mutation work to `TransactionalPOPIAConsentLifecycleService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: consent lifecycle rollback: fail after consent/audit write and assert atomic rollback
- Static marker closure allowed: `False`

### ROUTE-TX-007-popia-create_export_request

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/popia.py:create_export_request` to delegate mutation work to `TransactionalPOPIAConsentLifecycleService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: consent lifecycle rollback: fail after consent/audit write and assert atomic rollback
- Static marker closure allowed: `False`

### ROUTE-TX-008-diagnostics-submit_diagnostic

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/diagnostics.py:submit_diagnostic` to delegate mutation work to `TransactionalDiagnosticResponseService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: response/mastery/audit rollback: fail after response or mastery update and assert atomic rollback
- Static marker closure allowed: `False`

### ROUTE-TX-009-diagnostics-start_diagnostic_session

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/diagnostics.py:start_diagnostic_session` to delegate mutation work to `TransactionalDiagnosticResponseService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: response/mastery/audit rollback: fail after response or mastery update and assert atomic rollback
- Static marker closure allowed: `False`

### ROUTE-TX-010-diagnostics-diagnostic_respond

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/diagnostics.py:diagnostic_respond` to delegate mutation work to `TransactionalDiagnosticResponseService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: response/mastery/audit rollback: fail after response or mastery update and assert atomic rollback
- Static marker closure allowed: `False`

### ROUTE-TX-011-lessons-generate_lesson

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/lessons.py:generate_lesson` to delegate mutation work to `TransactionalLessonCompletionService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: lesson completion/gamification rollback: fail after lesson progress or XP award and assert atomic rollback
- Static marker closure allowed: `False`

### ROUTE-TX-012-lessons-generate_lesson_stream

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/lessons.py:generate_lesson_stream` to delegate mutation work to `TransactionalLessonCompletionService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: lesson completion/gamification rollback: fail after lesson progress or XP award and assert atomic rollback
- Static marker closure allowed: `False`

### ROUTE-TX-013-lessons-get_lesson

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/lessons.py:get_lesson` to delegate mutation work to `TransactionalLessonCompletionService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: lesson completion/gamification rollback: fail after lesson progress or XP award and assert atomic rollback
- Static marker closure allowed: `False`

### ROUTE-TX-014-lessons-complete_lesson

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/lessons.py:complete_lesson` to delegate mutation work to `TransactionalLessonCompletionService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: lesson completion/gamification rollback: fail after lesson progress or XP award and assert atomic rollback
- Static marker closure allowed: `False`

### ROUTE-TX-015-lessons-sync_lessons

- Current status: `route-transaction-wiring-not-proven`
- Implementation: Refactor `app/api_v2_routers/lessons.py:sync_lessons` to delegate mutation work to `TransactionalLessonCompletionService` inside one transaction boundary instead of coordinating partial writes in the router.
- Negative test: lesson completion/gamification rollback: fail after lesson progress or XP award and assert atomic rollback
- Static marker closure allowed: `False`


## No false-closure rules

- Do not close route transaction wiring from static service-name markers.
- Do not close route transaction wiring from isolated rollback service tests alone.
- Do not close route transaction wiring until route-level negative tests exercise the production route path.
- Do not close live DB proof until a real database transaction rollback check is attached.

## Interpretation

This plan is an implementation queue. It does not prove route transaction wiring is complete.
