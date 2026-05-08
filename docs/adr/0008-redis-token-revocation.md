# ADR 0008: Redis Token Revocation

## Status
Proposed

## Context
JWT-based session flows need revocation, refresh-token rotation, abuse detection, and logout/session invalidation semantics that cannot be achieved with stateless tokens alone.

## Decision
Use Redis as the low-latency revocation/session coordination store for token identifiers, refresh-token rotation state, and short-lived abuse counters.

Expected properties:

- Expiring keys aligned with token lifetimes.
- Reuse detection for rotated refresh tokens.
- Explicit logout and administrative revocation support.
- Safe fallback behavior when Redis is unavailable, determined by endpoint risk.

## Consequences

- **Pros**: Fast revocation checks, straightforward TTL semantics, supports rate limiting/session controls.
- **Cons**: Adds infrastructure dependency and requires clear fail-open/fail-closed policy by route class.
