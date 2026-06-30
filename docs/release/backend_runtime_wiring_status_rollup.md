# Backend Runtime Wiring Status Rollup

**Status:** scoped runtime wiring helpers active

## Active scoped helpers

| Helper | Scope | Destructive? |
|---|---|---|
| `first_audit_runtime_wiring.py` | one audit candidate | no |
| `first_consent_runtime_wiring.py` | one consent candidate | no |
| `first_deep_readiness_runtime_wiring.py` | read-only readiness plan | no |

## Remaining blockers

Real DB schema proof, real staging smoke, CI evidence, and release-owner approval remain pending.
