---
title: "ADR 0010 — Business Logic Location"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR 0010 — Business Logic Location

**Status:** Accepted
**Date:** 2026-05
**Deciders:** EduBoost SA V2 core team
**Relates to:** Backlog §2.2, PR-ARCH §2.1

---

## Context

The V2 codebase has two candidate homes for application-layer business logic:

1. `app/services/<context>_service.py` — flat service files at the `app` root level.
2. `app/modules/<context>/service.py` — a module directory per bounded context, co-locating
   the service with its domain models, repositories, and tests.

Both patterns exist in the repository today, creating confusion about where new logic
should be placed and making static import-boundary enforcement harder.

---

## Decision

**`app/services/<context>_service.py` is the canonical location for V2 business logic.**

`app/modules/` is reserved for self-contained learning engines (CAPS item-bank,
diagnostics engine, adaptive hint ML layer) that carry their own domain models and
have no peer dependencies on other services. These are *modules*, not service duplicates.

### Rules

| Rule | Detail |
|---|---|
| One service file per bounded context | `app/services/auth_service.py`, `app/services/learner_service.py`, etc. |
| Services orchestrate domain operations | No SQL in services; all persistence via repositories |
| Modules are self-contained engines | `app/modules/diagnostics/`, `app/modules/lessons/`, `app/modules/caps/` |
| Modules expose a clean public API | Callers import from `app.modules.<name>.api`, not internal submodules |
| No duplicate concepts | If a service and a module cover the same context, consolidate into the service and have the module delegate |

---

## Consequences

**Positive**
- Single authoritative location for each bounded context's workflow logic.
- Import-linter can enforce `routers → services → repositories` without ambiguity.
- Onboarding developers have one place to look.

**Negative / trade-offs**
- Existing module-level service files must be consolidated; see §2.2 collapse tasks.
- Modules that currently duplicate service concerns need a deprecation window.

---

## Migration Path

1. Inventory `app/services/` and `app/modules/` (backlog §2.2 P1 tasks).
2. For each duplicate concept: keep the `app/services/` version as authoritative;
   have the module delegate to it or be collapsed into it.
3. Add `# DEPRECATED: use app.services.<x>_service` headers to files being retired.
4. Remove deprecated paths after one sprint stabilisation period.

---

## Alternatives Considered

**Module-first (rejected):** Moving all logic into `app/modules/<context>/service.py`
would require restructuring the entire codebase and make the flat `app/services/`
import boundary harder to enforce with `import-linter`.

**Dual-track (rejected):** Allowing both patterns permanently creates the exact
ambiguity this ADR is resolving.
