# Deep Readiness Route Contract Slice 002

**Status:** read-only route contract catalogue active

## Scope

This slice defines a catalogue of deep-readiness checks and explicitly separates public-safe read-only checks from internal mutating probes.

## Guardrails

- Public deep readiness checks must not mutate database state.
- Mutating audit probes are internal-only and disabled by default.
- Runtime route wiring is deferred.
