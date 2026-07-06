---
title: "KG-5 Grounded Generation Schema"
status: authority_defined
---

# KG-5 Grounded Generation Schema

The generated pack contains:

- `lesson_drafts`: one graph-grounded lesson draft per KG-4 advisory intervention.
- `assessment_drafts`: one shadow exit-check item per lesson draft.
- `generation_edges`: provenance edges from intervention to lesson and lesson to
  assessment.

All generated records must include `source_ref`, `source_sha256`,
`gap_plan_sha256`, `target_graph_sha256`, `generation_preview_only: true`,
`human_review_required: true`, and `no_live_learner_data: true`.
