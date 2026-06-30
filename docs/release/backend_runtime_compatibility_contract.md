# Backend Runtime Compatibility Contract

This contract defines the runtime-facing invariants that must hold before backend consolidation proceeds from diagnostics into implementation.

## Audit repository canonical interface

The canonical audit path must support security/POPIA event recording with this minimum event shape:

| Field | Requirement |
|---|---|
| `action` | required |
| `actor_id` | optional but expected for user/system actions |
| `resource_type` | optional but recommended |
| `resource_id` | optional but recommended |
| `payload` / `metadata` | structured dictionary |

Legacy audit calls may use `append(...)`, but they must be adaptable into canonical `record(...)` semantics before legacy deletion.

## Consent service runtime interface

Consent runtime paths must support:

| Operation | Required behavior |
|---|---|
| active consent read | deterministic allow/deny response |
| grant/revoke | emits canonical audit-compatible event |
| POPIA service construction | does not require ambiguous repository wiring |
| data-rights operations | preserve explicit read/write authorization boundaries |

## Deep-health evidence interface

Deep health/readiness must eventually report:

- database connectivity
- Alembic current/head information
- required table presence
- audit persistence availability
- consent persistence availability
- no public unsafe write operations

This batch adds evidence checks only. Runtime route changes must be implemented separately.
