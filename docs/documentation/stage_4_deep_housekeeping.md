---
title: Stage 4 Documentation Deep Housekeeping
status: active
owner: documentation-governance
reviewers: [architecture, product, backend, privacy, security, release-management]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 30
evidence_command: make docs-housekeeping-stage4-check
code_anchors: [scripts/maintenance/check_doc_stage4_strict_scope.py, docs/documentation/stage_4_strict_scope.json]
---

# Stage 4 Documentation Deep Housekeeping

Stage 4 expands strict documentation enforcement from the Stage 3 governance/ADR scope into the first active product and engineering documentation areas.

## Scope

Stage 4 covers:

- `docs/architecture/`
- `docs/product/`
- `docs/api/`
- `docs/compliance/`
- `docs/security/`

The tranche adds required metadata, fixes active broken links, normalizes duplicate API redirect titles, and promotes these directories into strict-scope validation.

## Required commands

```bash
make docs-housekeeping-stage4-check
make docs-housekeeping-check
```

## Closure rule

Stage 4 is closable only when the Stage 4 strict-scope check and the default housekeeping gate pass from a clean checkout or ZIP extraction without inventory mutation inside the validation target.
