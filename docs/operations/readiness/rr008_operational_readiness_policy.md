---
title: "RR-008 Operational Readiness Policy"
status: authority
owner: operations
audience: developer, operator
---

# RR-008 Operational Readiness Policy

**RR item:** RR-008

Operational readiness is the canonical evidence layer for runbook linkage, learner-journey SLOs, capacity assumptions, LLM cost controls, and Grafana/alert linkage.

## Required readiness areas

- Incident response runbook index recorded.
- SLO definitions recorded.
- Capacity planning recorded.
- LLM cost model recorded.
- Grafana alert linkage recorded.

## Caveats carried forward

- `RR-003` remains valid, but its fallback coverage baseline recorded `0.0` because full test collection had pre-existing blockers.
- `RR-006` remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.

## Boundary

- Production release is not authorised.
- Deployment is not authorised.
- Release tagging is not authorised.
- Public beta is not authorised.
- Runtime KG implementation is not authorised.

## Relationship to RR-016

RR-008 records operational readiness documentation and linkage. It does **not** execute backup, restore, rollback, or incident handoff drills. Those drill proofs remain outstanding under `RR-016`.
