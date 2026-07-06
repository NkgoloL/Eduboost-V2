---
title: RR-003 — Coverage / CI / Route Authority
status: active-control
owner: roadmap-reconciliation
reviewers: [roadmap-reconciliation, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# RR-003 — Coverage / CI / Route Authority

**RR item:** RR-003  
**Priority:** P0  
**Source:** `docs/roadmap/roadmap.md` Phase 9  
**Status:** authority installed / evidence pending

## Purpose

RR-003 closes the roadmap gap around current coverage evidence, release-visible CI checks, and route-prefix authority.

## Scope

This slice establishes:

- Coverage baseline required before release claims.
- Coverage threshold must be decided and recorded with evidence.
- Release-blocking checks must be visible in CI.
- `/api/v2` is the canonical API prefix.
- `/v2` is compatibility-only and must be managed by the route alias matrix.
- Dormant routers must be inventoried before retirement or archival work.
- Release evidence must point at current evidence rather than historical claims.

## Not in scope

This slice does not authorise production release, deployment, public beta, release tagging, runtime KG implementation, or new product work.

## Closure criteria

RR-003 evidence is valid only when:

1. Current coverage is regenerated and recorded.
2. A threshold is recorded for the release baseline.
3. Route alias policy check passes.
4. CI workflow exposes release-authority checks.
5. Dormant router inventory exists.
6. Release authority docs and evidence are checksummed.
