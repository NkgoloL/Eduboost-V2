---
title: Technical Audit Remediation — Baseline Reset
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

# Technical Audit Remediation — Baseline Reset

**Status:** implementation baseline reset
**Position:** post-Phase-02R closure
**Purpose:** restart the broader technical-audit remediation stream after the Phase 02R authoritative corpus, grounded generation, and tutor retrieval reset.

## Control statement

Phase 02R is terminally closed and must not be reopened for general release-readiness work. The technical-audit stream now resumes with a separate remediation register, separate evidence, and separate closure criteria.

This baseline reset addresses the first set of contract blockers that can be repaired without live database execution:

1. Frontend/backend POPIA data-rights route drift.
2. Parent dashboard privacy export URL drift.
3. Frontend production API fallback to a hosted backend.
4. Dependency-scan workflow summary drift after pnpm migration.
5. Missing audit-remediation verifier and evidence collection harness.

## Explicit non-scope

This baseline reset does not claim:

- full product release readiness;
- OpenAPI regeneration completion;
- full backend fast-test closure;
- full frontend, E2E, migration, or deployment gate closure;
- live database execution;
- completion of the full 13-phase remediation stream.

## Required evidence after implementation

Evidence is written under:

```text
docs/release-evidence/technical-audit/baseline-reset/
```

Required artifacts:

```text
raw/baseline_reset.json
raw/popia_route_contract.json
raw/frontend_env_contract.json
raw/dependency_scan_workflow.json
raw/unit_tests.txt
raw/compileall.txt
raw/SHA256SUMS.txt
evidence_index.md
```
