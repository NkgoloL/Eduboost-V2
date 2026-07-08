#!/usr/bin/env python3
"""Apply PRD-0.8 branch/release naming reconciliation.

The script only refreshes the canonical branching policy document. It does not
rename repository branches, rewrite historical workflow compatibility triggers,
create release tags, or enable deployment.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

BRANCHING_DOC = Path("docs/engineering/branching.md")

BRANCHING_DOC_TEXT = """# Branching and Release Naming Policy

**Owner:** Platform / Engineering
**Status:** Canonical after PRD-0.8
**Last updated:** 2026-07-08
**Control record:** `docs/roadmap/production_readiness/prd_008_branch_release_naming_reconciliation_record.json`

---

## Current canonical branch

EduBoost currently uses `master` as the protected trunk branch for controlled production-readiness work.

| Name | Status | Purpose |
|---|---|---|
| `master` | Canonical protected trunk | Source of truth for merged PRD evidence and authority records. |
| `main` | Legacy compatibility alias only | May appear in historical workflows or archived documentation, but is not the current protected trunk. |
| `release/**` | Reserved release branch pattern | May be referenced by historical release workflows, but does not authorise production release by itself. |
| `codex/prd-*` | Short-lived PRD work branches | Used for authority/evidence PRs and merged back to `master`. |

This document replaces older references that described `main` as the production trunk. Any remaining `main` references must be interpreted through the PRD-0.8 inventory as historical/compatibility references unless a later approved slice changes the repository default branch.

---

## Release naming and authority boundary

PRD-0.8 is a naming reconciliation slice only. It does **not** authorise:

- production release;
- deployment;
- release tag creation;
- public beta traffic;
- live learner traffic;
- billing launch;
- live payment processing;
- PRD-1 implementation; or
- a new KG roadmap slice.

The current controlled runtime KG authority switch remains active because it was already authorised and closed before this stream.

---

## PRD branch convention

Use this convention for production-readiness stream work:

| Branch kind | Pattern | Example |
|---|---|---|
| Authority branch | `codex/prd-<nnn>-<slice-slug>` | `codex/prd-008-branch-release-naming-reconciliation` |
| Evidence branch | `codex/prd-<nnn>-<slice-slug>-evidence` | `codex/prd-008-branch-release-naming-reconciliation-evidence` |
| Protected trunk | `master` | `master` |

Authority PRs must land before evidence capture. Evidence capture must run from clean, synced `master` after the authority PR lands.

---

## Release branch pattern

`release/**` remains a reserved pattern for future release work. A branch name matching `release/**` is not enough to release EduBoost. Release authority remains blocked until the later approved production-readiness slices explicitly authorise it.

---

## Validation

Run:

```bash
PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd008_branch_release_naming_reconciliation.py --json
```

Expected state after PRD-0.8 evidence capture:

```text
canonical trunk branch: master
next authorised item: PRD-0.9
production release authorised: false
release tag authorised: false
deployment authorised: false
```
"""


def apply(root: Path = Path("."), write: bool = False) -> dict:
    path = root / BRANCHING_DOC
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    changed = current != BRANCHING_DOC_TEXT
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(BRANCHING_DOC_TEXT, encoding="utf-8")
    return {
        "branching_policy_path": str(BRANCHING_DOC),
        "changed": changed,
        "canonical_trunk_branch": "master",
        "legacy_main_alias_policy": "compatibility-only",
        "release_branch_pattern": "release/**",
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = apply(Path(args.root), write=args.write)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.8 branching policy checked. changed={result['changed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
