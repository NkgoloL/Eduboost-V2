---
title: "ADR-001 — Supported Python Runtime Version"
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
# ADR-001 — Supported Python Runtime Version

**Status:** Accepted
**Date:** 2026-05-27 (Phase 0 T060)
**Decision owner:** Platform / Engineering
**Supersedes:** none

---

## Context

The 2026-05-27 Technical State Audit observed conflicting Python runtime
declarations across the project:

| Surface | Declared version |
|---|---|
| Local developer `.venv` | 3.12.3 |
| `.python-version` (pyenv) | 3.11.10 |
| `render.yaml` `PYTHON_VERSION` | 3.11.9 |
| `README.md` | "Python 3.11+" |
| CI workflows (`.github/workflows/*.yml`) | mix of `"3.11"`, `"3.11.10"`, and `"3.12"` |
| System Python (`/usr/bin/python3`) | 3.14.5 (incompatible with project deps) |

The drift caused import failures when developers ran scripts outside the
project's `.venv` (system Python 3.14 broke `asyncpg` and other native
extensions). It also creates ambiguity about which Python version production
actually runs on Render.

This ADR resolves the ambiguity by declaring a single supported runtime and
binding every surface to it.

---

## Decision

**The single supported Python runtime for EduBoost V2 is Python 3.12.**

The pinned patch version is **3.12.3** at the time of this ADR. The patch
version is bumped only by a follow-up ADR or a documented `patch-bump` PR.

### Rationale

1. **Local developer environment is already on 3.12.3.** Forcing a downgrade
   to 3.11 would require every contributor to rebuild their virtualenv and
   reinstall native dependencies, with no compensating benefit.
2. **Roughly half of CI workflows are already on 3.12.** Standardising on the
   higher minor version requires fewer net workflow edits than downgrading
   the 3.12 workflows to 3.11.
3. **3.12 brings tangible runtime gains for a FastAPI workload:** improved
   `asyncio` scheduler behaviour, faster comprehensions, reduced
   per-coroutine memory.
4. **Render supports Python 3.12** as a first-class runtime; no platform
   work is needed.
5. **System Python is explicitly out of scope.** Tooling such as system
   `pip3` or system `python3` shells must not be assumed compatible with
   project dependencies. All validation commands in this repository run
   from `.venv/bin/python` or the equivalent CI Python.

### Rejected alternatives

- **Lock to 3.11.10 (matching pre-audit `.python-version`).** Rejected
  because local `.venv` is already at 3.12.3, half of CI is on 3.12, and
  3.11 offers no benefit over 3.12 for a FastAPI workload.
- **Allow a range (e.g., `>=3.11,<3.13`).** Rejected because the audit's
  primary complaint was *ambiguity*. A range substitutes one form of
  ambiguity for another and does not constrain Render or CI to a single
  version.
- **Lock to 3.13.** Rejected because not all transitive dependencies have
  published wheels for 3.13 at the audit date, and CI runners would need
  to install from source for some packages.

---

## Consequences

### Required changes (applied in T061)

| File | Change |
|---|---|
| `.python-version` | `3.11.10` → `3.12.3` |
| `render.yaml` | `PYTHON_VERSION: "3.11.9"` → `PYTHON_VERSION: "3.12.3"` |
| `README.md` | "Python 3.11+" → "Python 3.12 (managed via `.python-version`; currently 3.12.3)" |
| `.github/workflows/*.yml` | every `python-version:` value → `"3.12.3"` |

### Developer responsibilities

- Developers running an older `.venv` must recreate it:
  ```bash
  rm -rf .venv
  python3.12 -m venv .venv
  .venv/bin/pip install -r requirements/dev.txt
  ```
- Any new workflow added to `.github/workflows/` must set
  `python-version: "3.12.3"`. The CI workflow audit (T140) will check for
  this.

### Bumping the patch version

A patch bump (e.g., 3.12.3 → 3.12.4) requires:

1. A PR titled `runtime: bump python patch to 3.12.X` that updates every
   surface listed above in a single change.
2. A clean run of the full CI suite on the new patch.
3. A note appended to this ADR under a `## Revision history` section.

A minor bump (3.12 → 3.13) requires a new ADR superseding this one, not a
patch-bump PR.

---

## Validation

After T061 is applied, the following commands must all report the same
declared version:

```bash
cat .python-version
grep -E "^\s+value: \"3\." render.yaml
grep -E "python-version" .github/workflows/*.yml | sort -u
```

All three must show `3.12.3` (or list the same version everywhere with no
mix).
