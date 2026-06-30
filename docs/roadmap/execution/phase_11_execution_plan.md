# Phase 11 Execution Plan — Technical Debt Burn-Down

**Date**: 2026-06-12
**Updated**: 2026-06-14
**Status**: Partial; Ruff target deferred, other debt gates evidenced
**Branch**: `phase-11/technical-debt-burn-down`
**Base**: `origin/master`
**Source**: `docs/roadmap/roadmap.md` § Phase 11
**Scope**: Burn down the four categories of tracked technical debt: Ruff findings, import-linter violations, route comment hygiene, migration audit, and dormant router cleanup.

---

## 2026-06-14 Audit Note

Phase 11 now has current evidence for import-linter compliance, route-comment
hygiene, migration audit, and dormant-router cleanup. The original Ruff target
of `<=100` findings remains unmet: current non-blocking Ruff debt is 650
findings, mostly E402 import-order and E701/E702 style findings.

Fresh evidence is recorded in:

- `docs/release/phase_11_evidence.md`
- `docs/release/phase_11_implementation_audit.md`
- `docs/release/phase_11_route_comment_audit.md`
- `docs/database/migration_audit.md`

---

## Pre-Conditions

- [x] Phase 10 (Post-Production Product Documentation) merged to `master`
- [x] Phases 0–10 complete and verified
- [x] Branch `phase-11/technical-debt-burn-down` created from `master`
- [x] `docs/backlog/ruff_debt.md` baseline exists (2026-06-09, ~1,000 findings)
- [x] Import-linter config exists at `.importlinter` (3 contracts defined)
- [x] 36 Alembic migrations accumulated
- [x] Dormant router files still present: `ether.py`, `judiciary.py`

---

## Inventory of Remaining Debt

### I.1 — Ruff Findings (~1,000 non-blocking)

Release-blocking correctness gates (E9, F63, F7, F82, F821) are **zero** and CI-gated. Remaining findings by category:

| Category | Rule(s) | Typical Issue | Estimated Count |
|----------|---------|---------------|-----------------|
| Unused imports/variables | F401, F841, F811 | Imported but never used | ~300 |
| Print statements | T201 | `print()` in production code | ~50 |
| Blank line / whitespace | W291, W292, W293 | Trailing whitespace, missing newline | ~200 |
| Line length | E501 | > 88 characters | ~150 |
| Docstring conventions | D100–D417 | Missing or malformed docstrings | ~200 |
| Naming conventions | N801–N815 | Class/function naming style | ~50 |
| SIM rules | SIM101–SIM401 | Simplify boolean/if-else patterns | ~50 |

### I.2 — Import-Linter Boundary Violations

3 contracts defined in `.importlinter`:
- `api_v2_routers_do_not_import_repositories`
- `popia_router_uses_dependency_layer`
- `lessons_router_uses_authorization_service_layer`

### I.3 — Route Comment Drift

Comments in route handlers may reference outdated dependency injection patterns (e.g., "trust the lesson_id" comments).

### I.4 — Migration Audit

36 migrations accumulated, some pre-V2. Benefits of squashing:
- Faster `alembic upgrade head` from empty DB
- Cleaner migration history
- Removal of pre-V2 schema references

### I.5 — Dormant Router Files

Files that are no longer registered in `app/api_v2.py`:
- `app/api_v2_routers/ether.py`
- `app/api_v2_routers/judiciary.py`

---

## Work Groups

### I.1 — Ruff Findings Burn-Down [medium]

**Goal:** Reduce non-blocking Ruff findings from ~1,000 to ≤ 100.

- [ ] Capture live Ruff count via `ruff check --statistics` (baseline measurement)
- [ ] Fix all `F401` (unused import) findings
- [ ] Fix all `F841` (unused variable) findings
- [ ] Fix all `T201` (print statement) findings — replace with `logger.debug()` or remove
- [ ] Fix all `W291/W292/W293` (whitespace) findings
- [ ] Fix all `E501` (line length) findings where readable; add `# noqa: E501` for justified exceptions
- [ ] Fix high-signal `SIM` (simplify) findings
- [ ] Fix `N801–N815` naming convention violations
- [x] Re-run `ruff check --statistics` and record final count in `docs/backlog/ruff_debt.md`
- [x] Update `docs/backlog/ruff_debt.md` with new baseline and per-category results

**Evidence:** `ruff check --statistics` before/after, updated `docs/backlog/ruff_debt.md`  
**Risk:** Medium — 1,000 fixes is mechanical but tedious; use `ruff check --fix --unsafe-fixes` for automation

### I.2 — Import-Linter Compliance [medium]

- [x] Run `lint-imports` (or `make lint`) to surface current violations
- [x] Fix violations for each of the 3 contracts:
  - `api_v2_routers_do_not_import_repositories` — ensure routers use service layer, not repos directly
  - `popia_router_uses_dependency_layer` — ensure popia router uses consent/compat services
  - `lessons_router_uses_authorization_service_layer` — ensure lessons router uses auth services
- [x] For violations that cannot be fixed without refactoring, document exceptions in `.importlinter` with ADR reference

**Evidence:** Clean `make lint` run, exceptions documented in `.importlinter`  
**Risk:** Low — likely small number of violations

### I.3 — Route Comment Hygiene [low]

- [x] Audit all route handler docstrings and inline comments for accuracy:
  - `app/api_v2_routers/auth.py`
  - `app/api_v2_routers/consent.py`
  - `app/api_v2_routers/diagnostics.py`
  - `app/api_v2_routers/learners.py`
  - `app/api_v2_routers/lessons.py`
  - `app/api_v2_routers/parent_portal.py`
  - `app/api_v2_routers/popia.py`
  - `app/api_v2_routers/study_plans.py`
  - `app/api_v2_routers/gamification.py`
- [x] Fix or remove misleading comments
- [x] Ensure docstrings reference current dependency injection pattern (not legacy patterns)

**Evidence:** Updated route files  
**Risk:** Low — documentation-only changes

### I.4 — Migration Audit [low]

- [x] Identify pre-V2 migrations (before the V2 architectural migration commit)
- [x] Document migration audit at `docs/database/migration_audit.md`:
  - Total migration count (36)
  - Pre-V2 migration count
  - Squash recommendation (safe to squash? any data migrations?)
  - Current migration chain head
- [x] Evaluate whether a squash migration should consolidate pre-V2 migrations into a single baseline
- [x] Document the no-squash recommendation and retain existing migration verification targets

**Evidence:** `docs/database/migration_audit.md`  
**Risk:** Low — documentation and optional squash

### I.5 — Dormant Router Cleanup [low]

- [x] Verify `app/api_v2_routers/ether.py` is NOT registered in `app/api_v2.py`
- [x] Verify `app/api_v2_routers/judiciary.py` is NOT registered in `app/api_v2.py`
- [x] Archive both files to `archive/api_v2_routers/` (preserve git history)
- [x] Remove from working tree

**Evidence:** Files removed from `app/api_v2_routers/`, no import errors in `app/api_v2.py`  
**Risk:** Very low — dead code removal

---

## Execution Order

```
Week 1:  I.2 (import-linter) — quick fix, unblocks CI
         I.5 (dormant routers) — trivial
         I.3 (route comments) — read-through, quick fixes
Week 2:  I.4 (migration audit) — investigation + documentation
         I.1 (Ruff burn-down) — automated + manual fixes, most time-consuming
         Repeat: ruff check --fix → review → commit → repeat
```

---

## Definition of Done

- [ ] Ruff findings reduced from ~1,000 to ≤ 100 (recorded in `ruff_debt.md`)
- [ ] `make lint` passes (import-linter contracts satisfied)
- [x] Route comments audited and fixed for accuracy
- [x] `docs/database/migration_audit.md` documents migration status and squash recommendation
- [x] Dormant router files archived or removed
- [x] Implementation report written
- [x] PR merged to `master`
