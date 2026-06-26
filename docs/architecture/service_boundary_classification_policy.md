---
title: "Service Boundary Classification Policy"
status: active
owner: architecture
reviewers: [architecture, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/architecture/README.md]
---

# Service Boundary Classification Policy

**Status:** active

## Rule

Do not delete `app/services/` wholesale. After the P0 runtime repairs, that package contains active cross-cutting runtime facades and authorization helpers.

## Classifications

| Classification | Meaning | Action |
|---|---|---|
| `active_runtime_facade` | Runtime helper or facade used by repaired routers/services | Keep |
| `authorization_helper` | Cross-cutting authz helper | Keep or move deliberately |
| `canonical_domain_service` | Current domain service implementation | Keep |
| `deprecated_legacy_service` | Old implementation pending call-site removal | Migrate/delete after proof |
| `migration_or_compat_helper` | Transitional adapter/helper | Keep until migration complete |
| `duplicate_domain_service` | Competing domain implementation | Resolve in targeted refactor |
| `unclassified` | Needs manual classification | Review |

## Enforcement

Repaired P0 routers must not import `app.repositories` directly. New router repository imports must go through service/dependency layers unless explicitly allowlisted with a dated migration note.
