---
title: "Test/dependency bootstrap baseline schema"
status: "active"
owner: "product"
reviewers: ['product', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Test/dependency bootstrap baseline schema

The evidence capture writes:

```text
docs/roadmap/production_readiness/test_dependency_bootstrap_baseline.json
```

Required top-level fields:

- `schema_version`
- `prd_id`
- `captured_at`
- `python_backend`
- `frontend`
- `workflow_inventory`
- `bootstrap_contracts`
- `deferred_to_later_prd0_slices`
- `authority_boundaries`

The baseline is descriptive evidence. It does not authorise production release, deployment, public beta, billing, or PRD-1 implementation.
