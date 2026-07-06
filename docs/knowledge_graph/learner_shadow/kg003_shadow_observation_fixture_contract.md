---
title: "KG-3 Shadow Observation Fixture Contract"
status: active
owner: knowledge-graph
---

# KG-3 Shadow Observation Fixture Contract

The KG-3 fixture is a synthetic input used to exercise learner graph shadow construction.

Contract:

- Learner aliases must start with `kg3-synthetic-`.
- The fixture must state `uses_live_learner_data: false`.
- The fixture must state `contains_pii: false`.
- The fixture must be committed as source input, not generated evidence.
- The generated learner shadow graph must carry the fixture SHA-256 on every shadow state and event.
