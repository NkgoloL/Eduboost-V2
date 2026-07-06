---
title: "KG-8 Post-Switch Review Schema"
status: active
---

# KG-8 Post-Switch Review Schema

The generated pack contains:

- `optimisation_candidates[]`
- `scale_review_checks[]`
- `monitoring_requirements[]`
- `rollback_observability_checks[]`
- `post_switch_review_edges[]`
- `boundary{}`
- `counts{}`

Every generated item must include:

- `key`
- `id`
- `name`
- `kind`
- `priority`
- `status`
- `post_switch_review_only: true`
- `source_ref`
- `source_sha256`
- `version`

No generated item may include live learner data, guardian PII, payment data, or production deployment instructions.
