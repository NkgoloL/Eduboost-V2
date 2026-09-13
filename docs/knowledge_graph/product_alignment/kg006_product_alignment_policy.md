---
title: "KG-6 Product Alignment Policy (Kg006 Product Alignment Policy)"
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
# KG-6 Product Alignment Policy

KG-6 may create only synthetic, non-authoritative preview records for product surfaces. It must not change live tutor behaviour, assign badges, alter study plans, expose guardian data, or persist learner graph state.

Required controls:

- Use only the KG-5 generation pack as input.
- Do not use live learner or guardian records.
- Keep every product alignment item advisory-only and preview-only.
- Require human review before any learner-facing or guardian-facing use.
- Keep runtime authority, database migration, public beta, deployment, and production release boundaries false.
