---
title: "Import Boundaries"
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

# Import Boundaries

EduBoost SA V2 enforces strict layered import boundaries using
[`import-linter`](https://import-linter.readthedocs.io/). All contracts are
declared in `.importlinter` at the repository root and are checked in CI on
every PR.

---

## Allowed Dependency Direction

```
app.api_v2_routers
        │
        ▼
app.services   ←→   app.modules  (services may call module public APIs; modules must not call services)
        │
        ▼
app.repositories
        │
        ▼
app.domain   +   app.core
        │
        ▼
  stdlib / third-party packages
```

Arrows point **down only**. No upward or sideways imports are permitted
between layers.

---

## Contract Summary

| Contract | Source | Forbidden target | Rationale |
|---|---|---|---|
| `routers-no-repositories` | `app.api_v2_routers` | `app.repositories` | Routers must go through services |
| `routers-no-domain-writes` | `app.api_v2_routers` | `app.domain` (write models) | Routers map to/from Pydantic request/response schemas only |
| `services-no-routers` | `app.services` | `app.api_v2_routers` | No upward dependency |
| `services-no-fastapi-request` | `app.services` | `fastapi.Request` | Services must not depend on HTTP transport |
| `modules-no-routers` | `app.modules` | `app.api_v2_routers` | Modules are transport-agnostic |
| `modules-no-services` | `app.modules` | `app.services` | Modules are self-contained engines |
| `repositories-no-routers` | `app.repositories` | `app.api_v2_routers` | No upward dependency |
| `repositories-no-services` | `app.repositories` | `app.services` | No upward dependency |
| `domain-no-infrastructure` | `app.domain` | `app.repositories`, `app.core.db` | Domain is pure data contracts |

---

## Allowed Cross-Layer Calls

- Routers **may** import from `app.services`, `app.domain`, `app.core`.
- Services **may** import from `app.repositories`, `app.domain`, `app.core`, and
  module public APIs (`app.modules.<name>.api`).
- Modules **may** import from `app.repositories`, `app.domain`, `app.core`.

---

## Running the Check Locally

```bash
lint-imports
```

Or via Make:

```bash
make lint-imports
```

---

## Adding a New Contract

1. Add the contract block to `.importlinter`.
2. Update this document's contract summary table.
3. Run `lint-imports` locally to confirm the new contract passes before pushing.
