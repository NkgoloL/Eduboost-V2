---
title: Stage 3 Documentation Housekeeping
status: active
owner: documentation-governance
reviewers: [engineering, architecture, release-management]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 30
evidence_command: make docs-housekeeping-stage3-check
code_anchors: [scripts/maintenance/check_doc_stage3_strict_scope.py, docs/documentation/stage_3_strict_scope.json]
---

# Stage 3 Documentation Housekeeping

Stage 3 converts the documentation cleanup programme from global ratchets into the first passing strict tranche.

## Scope

Stage 3 tranche 1 covers:

- root `README.md` metadata;
- canonical documentation governance files under `docs/documentation/`;
- active ADR files under `docs/adr/` and `docs/adr/frontend/`;
- duplicate root-level ADR number cleanup;
- local link validation for the strict scope;
- consolidated documentation-governance workflow enforcement.

This does not claim the full documentation corpus is clean. Historical, generated, evidence, and legacy areas remain governed by Stage 2 ratchets until future strict tranches migrate them.

## Required commands

```bash
make docs-housekeeping-stage3-check
make docs-housekeeping-check
```

## Closure rule

Stage 3 tranche 1 is closable only when both commands pass from a clean checkout or source ZIP extraction without regenerating inventory inside the validation target.
