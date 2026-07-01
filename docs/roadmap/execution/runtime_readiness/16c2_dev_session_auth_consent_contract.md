# Phase 16C-2 — Dev-Session Auth and Consent Contract Repair

**Status:** repair harness installed; evidence unclaimed.

## Purpose

Align local non-production `/auth/dev-session` with the same runtime
authorization and consent gates used by real learner-scoped endpoints.

## Repairs

- Normalise enum roles such as `UserRole.PARENT` to the stable JWT/API value
  `parent`.
- Ensure dev-session consent uses the canonical runtime policy version
  `1.0.0`.
- Normalise stale active dev-session consent rows in place to avoid partial
  unique-index collisions.

## Boundary

This slice is dev-session contract repair only. It does not claim Phase 16
seeded E2E evidence or any production release/deployment authority.
