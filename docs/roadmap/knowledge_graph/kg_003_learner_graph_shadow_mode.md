---
title: "KG-3 Learner Graph Shadow Mode"
status: pending-evidence
owner: knowledge-graph
---

# KG-3 Learner Graph Shadow Mode

KG-3 derives a non-authoritative learner shadow graph from the approved KG-2 target graph and a synthetic observation fixture.

## Scope

- Build a learner shadow graph read-model artifact for Grade 4 Mathematics.
- Use only synthetic, non-identifying fixture observations.
- Preserve target graph provenance for every learner shadow state.
- Keep learner graph persistence, runtime KG authority, database migration, and learner-facing model changes out of scope.

## Exit criteria

- KG-2 target graph generation is valid.
- The synthetic observation fixture is recorded and explicitly excludes live learner data.
- The learner shadow graph artifact is generated.
- Every learner shadow state references an approved KG-2 target state.
- Every learner shadow state and event carries fixture/source provenance.
- Boundary flags remain false for runtime authority switch, database migration, learner-facing changes, and production/public release.
