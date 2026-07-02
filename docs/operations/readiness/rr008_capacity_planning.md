---
title: "RR-008 Capacity Planning"
status: authority
owner: operations
---

# RR-008 Capacity Planning

Capacity planning recorded: true

## Initial capacity assumptions

| Area | Controlled beta assumption | Scaling trigger |
|---|---:|---|
| Active learner cohort | bounded controlled beta cohort only | cohort expansion approval |
| Concurrent learners | low double digits | sustained p95 latency breach |
| Diagnostics traffic | burst at session start | diagnostic queue or DB latency trend |
| Lesson generation | guarded by AI gateway and cache policy | LLM cost or latency breach |
| Parent portal | lower concurrency than learner sessions | parent report latency trend |

## Capacity checks

- Confirm Postgres and Redis readiness before live beta windows.
- Confirm API `/ready` and deep health endpoints before learner sessions.
- Confirm monitoring dashboard and alert routing before expansion.
- Record capacity expansion decisions before increasing cohort size.

## Boundary

Capacity planning does not authorise expanded learner migration or public beta.
