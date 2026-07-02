---
title: "Stage 5 Technical Delivery and Learning-Engine Documentation Housekeeping"
status: active
owner: documentation-governance
reviewers: [engineering, operations, curriculum, ai-safety, quality]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 30
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [docs/documentation/stage_5_strict_scope.json, scripts/maintenance/check_doc_stage5_strict_scope.py]
---

# Stage 5 Technical Delivery and Learning-Engine Documentation Housekeeping

Stage 5 expands strict documentation housekeeping beyond the Stage 4 canonical architecture/product/API/compliance/security tranche.

## Scope

Strict enforcement now covers technical delivery and learning-engine documentation:

- `docs/frontend/`
- `docs/backend/`
- `docs/database/`
- `docs/deployment/`
- `docs/testing/`
- `docs/observability/`
- `docs/disaster_recovery/`
- `docs/operations_support/`
- `docs/runbooks/`
- `docs/content_factory/`
- `docs/caps/`
- `docs/curriculum/`
- `docs/diagnostics/`
- `docs/irt/`
- `docs/learning_science/`
- `docs/ai/`

## Gate

Run:

```bash
make docs-housekeeping-stage5-check
make docs-housekeeping-check
```

The global strict gate remains a future target. Stage 5 keeps the ratchet model: current scoped areas must stay clean, while release/evidence/archive debt is reduced in later tranches.
