---
title: Technical Audit Remediation Phase 02C — Backend Fast Scope Registry Expansion
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Technical Audit Remediation Phase 02C — Backend Fast Scope Registry Expansion

**Status:** Implementation package ready  
**Authority gate:** `make test-fast` remains blocked until it exits `0`  
**Primary blocker:** `grade5_mathematics_en` and generated scope registry entries missing from the file-backed Content Factory registry

## Objective

Restore the file-backed Content Factory registry so backend-fast tests can resolve the generated Grade 5 Mathematics scope and the broader generated curriculum scope set.

This slice addresses the dominant post-runtime-dependency backend-fast failure cluster without weakening the backend-fast authority gate.

## Scope

- Expand `data/content_factory/scopes.json` to the 51 generated topic-map scopes.
- Preserve `grade4_mathematics_en` as the only active learner-visible launch scope.
- Register every other generated scope as `review`, making it generation/staging-ready but not learner-visible.
- Register deterministic artifact paths for diagnostic items, lessons, assessment blueprints, and study-plan templates.
- Keep existing Grade 4 launch coverage targets unchanged.
- Update stale unit expectations that still described Grade 5 Mathematics as `planned`.
- Add audit-remediation verification and evidence scripts.

## Non-scope

- No passing backend-fast candidate evidence is created by this slice.
- No production learner visibility is expanded beyond Grade 4 Mathematics.
- No live DB migration is executed.
- No Phase 02R governance is changed.
- No runtime knowledge-graph implementation is added.

## KG monster boundary

The expanded registry preserves curriculum/source/artifact metadata that future KG work can consume, but it does not implement learner-state graphs, graph persistence, graph APIs, graph runtime retrieval, or graph-driven tutor behavior.

## Expected follow-up

After evidence is recorded for this slice, rerun:

```bash
bash scripts/audit_remediation/collect_backend_fast_evidence.sh
```

If `make test-fast` remains red, import failed-gate diagnostics and target the next largest failure cluster.
