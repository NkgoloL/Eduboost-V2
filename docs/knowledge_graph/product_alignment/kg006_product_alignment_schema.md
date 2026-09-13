---
title: "KG-6 Product Alignment Schema (Kg006 Product Alignment Schema)"
status: "active"
owner: "pedagogy"
reviewers: ['pedagogy', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# KG-6 Product Alignment Schema

The KG-6 evidence artifact contains:

- `tutor_previews`: shadow tutor alignment records mapped to KG-5 lesson drafts.
- `study_plan_items`: preview study-plan sequencing records mapped to KG-5 lesson drafts.
- `gamification_award_candidates`: badge/points candidates mapped to KG-5 assessment drafts.
- `parent_alignment_summaries`: synthetic guardian summary previews, without guardian PII.
- `product_alignment_edges`: traceability edges linking KG-5 draft items to KG-6 preview records.

Each record must include `source_ref`, `source_sha256`, `advisory_only: true`, `shadow_mode: true`, `preview_only: true`, `no_live_learner_data: true`, and `human_review_required: true` where applicable.
