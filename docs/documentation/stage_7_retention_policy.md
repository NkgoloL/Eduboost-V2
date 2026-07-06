---
title: Stage 7 Release Archive Retention Policy
status: active-policy
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

# Stage 7 Release Archive Retention Policy

This policy prevents deep-housekeeping from corrupting historical release and evidence records.

## Rules

1. Raw evidence files under `docs/release-evidence/**/raw/` are immutable evidence inputs and must not be mass-rewritten by documentation cleanup scripts.
2. Evidence index files are governed documents and may receive metadata and link/claim checks.
3. Historical release documents may retain historical readiness language when the Stage 7 strict-scope allowlist records the term and path.
4. Active roadmap, backlog, and codemap documents must avoid unbounded readiness claims unless tied to an evidence command and review boundary.
5. KG references remain allowed when they describe the architecture north star, codemap context, or future roadmap direction. Stage 7 must not claim runtime KG activation unless explicitly authorised by a separate implementation gate.

## Evidence command

```bash
make docs-housekeeping-stage7-check
```
