# Auth Lifecycle Method Extraction Repair Report

Generated at: `2026-05-18T16:23:42Z`

**Status:** implemented

## Delegated lifecycle methods


## Boundary

Routes now delegate through AuthApplicationService methods. Original route bodies are preserved as private `_auth_lifecycle_legacy_*_impl` helpers to avoid behavior changes while completing the service-boundary transition.

## Remaining debt

- Move private legacy helper bodies out of auth.py into AuthApplicationService proper.
- Add full HTTP request/response integration tests for register/login/refresh/dev-session.
