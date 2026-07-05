---
title: "KG-3 Learner Graph Shadow Privacy Boundary"
status: active
owner: knowledge-graph
---

# KG-3 Learner Graph Shadow Privacy Boundary

KG-3 is restricted to synthetic, non-identifying learner aliases. It must not export, ingest, or infer live learner PII.

Explicitly blocked in KG-3:

- production learner table reads;
- learner identifiers, names, contact details, guardian identifiers, or school identifiers;
- live diagnostic session exports;
- production learner graph training or retraining;
- learner-facing behavioural changes.
