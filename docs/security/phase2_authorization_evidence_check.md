# Phase 2 Authorization Evidence Check

## Purpose

This check consolidates the Phase 2 authorization evidence created so far.

It verifies that the authorization policy, dependency adapter, enforced pilot
routes, HTTP tests, and documentation are present and wired.

## Command

```bash
make phase2-authz-check
```

Equivalent direct command:

```bash
python3 scripts/check_phase2_authorization_evidence.py
```

## Scope

The checker covers:

- object authorization policy,
- FastAPI authorization dependency adapter,
- learner read route,
- learner mastery read route,
- study-plan write route,
- lesson-generation write route,
- diagnostic-items read route,
- associated HTTP tests and docs.

## Non-Goal

This check does not claim all Phase 2 authorization work is complete. It is an
evidence gate for the endpoints already migrated.
