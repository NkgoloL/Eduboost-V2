---
title: RR-005 Technical Debt Burn-Down
status: authority
owner: engineering
reviewers: [roadmap-reconciliation, release-management, documentation-governance]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# RR-005 Technical Debt Burn-Down

**RR item:** RR-005  
**Register source:** `docs/roadmap/reconciliation/outstanding_work_register.md`  
**Canonical area:** Technical debt burn-down

## Scope

RR-005 records the current technical-debt position before additional product or architecture work is introduced.

It covers:

- current Ruff debt inventory;
- import-linter exception register;
- stale route-comment audit;
- migration-history audit and squash decision;
- dormant router review and retirement boundary.

## Non-goals

- Do not remove active routes without call-site proof.
- Do not squash or rewrite Alembic history outside a dedicated migration window.
- Do not broaden runtime KG implementation.
- Do not authorise production release, deployment, release tags, or public beta.

## Closure rule

RR-005 is closed only when `rr_005_technical_debt_burndown_record.json` records all required evidence flags and the verifier returns `valid: true` from clean `master`.
