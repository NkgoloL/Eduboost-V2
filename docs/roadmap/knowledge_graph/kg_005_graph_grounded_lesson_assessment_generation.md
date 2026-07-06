---
title: "KG-5 Graph-Grounded Lesson and Assessment Generation"
status: authority_defined
kg_id: KG-5
requires: KG-4
---

# KG-5 Graph-Grounded Lesson and Assessment Generation

KG-5 converts the approved KG-4 advisory gap/intervention plan into a
source-grounded lesson-and-assessment generation pack for Grade 4 Mathematics.

The slice is deliberately non-authoritative. It creates reproducible preview
artifacts from synthetic shadow-mode evidence only. It does not call an LLM
provider, persist learner graph state, change learner-facing behaviour, or
switch any runtime KG authority.

## Inputs

- KG-4 advisory gap/intervention plan.
- KG-2 Grade 4 Mathematics target graph.

## Outputs

- Graph-grounded lesson drafts.
- Shadow assessment item drafts.
- Generation edges linking KG-4 interventions to KG-5 lesson and assessment
  outputs.
- Evidence proving the pack is source-grounded, preview-only, review-gated, and
  free of live learner data.

## Exit criteria

- KG-4 verifier is valid.
- The generation pack is generated from the KG-4 plan.
- Every lesson draft references a KG-4 intervention.
- Every assessment draft references a KG-5 lesson.
- Every generated item is source-grounded and human-review gated.
- Runtime KG, database migration, learner-facing model changes, LLM provider
  calls, production release, deployment, and public beta authority remain false.
