---
title: Phase 17 — Controlled Beta Readiness Authority
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

# Phase 17 — Controlled Beta Readiness Authority

**Status:** Harness prepared  
**Scope:** Readiness evidence aggregation only  
**Owner:** Nkgolo Lebelo

## Purpose

Phase 17 records that EduBoost has a controlled-beta readiness baseline after:

- technical-audit remediation closure,
- protected-branch post-merge baseline,
- live Postgres/Redis/API readiness,
- backend-backed smoke E2E readiness,
- backend-backed seeded E2E readiness.

This is not a production release gate and not a beta-launch approval gate.

## Required inputs

The capture script requires these verifiers to return `valid: true`:

```text
scripts/technical_audit/verify_technical_audit_closure.py --json
scripts/technical_audit/verify_post_merge_baseline.py --json
scripts/runtime_readiness/verify_live_stack_readiness.py --json
scripts/runtime_readiness/verify_backend_backed_e2e.py --json
scripts/runtime_readiness/verify_backend_backed_seeded_e2e.py --json
```

It also records the presence and checksums of key public/support documents:

```text
README.md
PRIVACY_NOTICE.md
SECURITY.md
CODE_OF_CONDUCT.md
```

## Boundary

The Phase 17 record must keep the following false:

```text
production_release_authorised
deployment_authorised
release_tag_authorised
public_beta_authorised
controlled_beta_launch_authorised
live_learner_traffic_authorised
learner_data_migration_authorised
runtime_kg_implementation_claimed
```

A later explicit beta-launch gate is required before any live learner traffic or deployment.
