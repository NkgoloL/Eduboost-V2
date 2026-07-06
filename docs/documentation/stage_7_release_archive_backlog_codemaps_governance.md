---
title: Stage 7 Release/Archive/Backlog/Codemaps Governance
status: active-control
owner: documentation-governance
reviewers: [documentation-governance, release-management, evidence-custodian]
audience: documentation-reviewer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 45
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/documentation/stage_7_strict_scope.json, scripts/maintenance/check_doc_stage7_strict_scope.py, scripts/maintenance/apply_doc_stage7_cleanup.py]
---

# Stage 7 Release/Archive/Backlog/Codemaps Governance

Stage 7 promotes the remaining release, archive, backlog, roadmap, codemap, reference, and beta-launch documentation surfaces into strict-scope governance.

## Scope

The tranche covers:

- `docs/release/`
- `docs/operations/`
- `docs/roadmap/`
- `docs/backlog/`
- `docs/codemaps/`
- `docs/roadmap_domains/`
- `docs/reference/`
- `docs/beta_launch/`
- `docs/archive/`
- `docs/release-evidence/**/evidence_index.md`

Raw evidence snapshots under `docs/release-evidence/**/raw/` are not rewritten by this tranche. Historical release and archive bodies are preserved as records; Stage 7 adds ownership, review metadata, evidence-index governance, and retention policy around them.

## KG boundary

EduBoost keeps the knowledge-graph direction as an architectural north star. Stage 7 does not activate runtime KG work and does not reinterpret historical release evidence as a runtime KG implementation. Codemaps and roadmap-domain documents may reference KG concepts only as architecture, roadmap, or evidence context.

## Enforcement

Run:

```bash
make docs-housekeeping-stage7-check
make docs-housekeeping-check
```

Stage 7 requires metadata, ASCII-safe filenames, scoped link validation, deterministic inventory, and retained historical-risk-term allowlists for archived/release evidence claims.
