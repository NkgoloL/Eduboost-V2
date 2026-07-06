---
title: "KG-4 Gap Engine and Intervention Planner"
status: pending-evidence
owner: knowledge-graph
---

# KG-4 Gap Engine and Intervention Planner

KG-4 compares the approved KG-3 learner shadow graph against the approved KG-2 target graph and generates a non-authoritative advisory gap profile with recommended intervention actions.

## Scope

- Build a Grade 4 Mathematics gap profile from KG-3 synthetic learner shadow states.
- Generate one advisory intervention recommendation per non-mastered shadow target.
- Preserve target, shadow-state, and source provenance for every gap item and recommendation.
- Keep all recommendations advisory-only and shadow-mode-only.
- Keep runtime authority, database migration, learner graph persistence, learner-facing model changes, production release, deployment, and public beta out of scope.

## Exit criteria

- KG-3 learner graph shadow mode is valid.
- The KG-4 gap/intervention plan artifact is generated.
- Every gap item references a KG-3 shadow state and approved target state provenance.
- Every intervention recommendation is source-grounded and advisory-only.
- No duplicate gap keys, duplicate intervention keys, or orphan planner edges exist.
- Boundary flags remain false for runtime authority, persistence, learner-facing changes, and release/deployment/public beta.
