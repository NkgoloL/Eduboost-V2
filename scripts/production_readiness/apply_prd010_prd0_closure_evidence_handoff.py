#!/usr/bin/env python3
"""Apply PRD-0.10 PRD-0 closure and PRD-1 handoff authority files.

This script creates authority documents and the initial PRD-0.10 record. It does
not capture closure evidence, modify live product behavior, implement PRD-1,
create release tags, deploy, or authorise production/beta/billing traffic.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PRD_ID = "PRD-0.10"
ROOT = Path("docs/roadmap/production_readiness")
PRD_DOC = ROOT / "prd_010_prd0_closure_evidence_handoff.md"
PLAN = ROOT / "prd0_closure_evidence_handoff_plan.md"
SCHEMA_DOC = ROOT / "prd0_closure_evidence_handoff.schema.md"
CHECKLIST = ROOT / "prd0_closure_handoff_checklist.md"
RECORD = ROOT / "prd_010_prd0_closure_evidence_handoff_record.json"
HANDOFF_DOC = Path("docs/engineering/prd0_to_prd1_handoff.md")

FALSE_BOUNDARIES = {
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
    "public_beta_live_traffic_authorised": False,
    "live_learner_traffic_authorised": False,
    "billing_launch_authorised": False,
    "live_payment_processing_authorised": False,
    "new_kg_slice_authorised": False,
    "prd1_implementation_authorised": False,
}
TRUE_BOUNDARIES = {
    "runtime_kg_implementation_claimed": True,
    "runtime_kg_authority_switch_authorised": True,
    "authority_switch_executed": True,
}

PRD_DOC_TEXT = """# PRD-0.10 — PRD-0 Closure Evidence and Handoff to PRD-1

**Stream:** PRD-PRODUCTION-READINESS  
**Status:** Authority slice; evidence capture required for closure  
**Owner:** Nkgolo Lebelo  
**Canonical trunk:** `master`

---

## Purpose

PRD-0.10 closes the PRD-0 post-closure current-state authority refresh stream and records the formal handoff to PRD-1 — Required CI and Release Gate Convergence.

This is the final PRD-0 slice. It proves that PRD-0.0 through PRD-0.9 are valid, records the closure evidence bundle, and updates the production-readiness register so that PRD-1 is the next authorised workstream.

---

## Explicit boundary

PRD-0.10 does not implement PRD-1. It does not standardise CI commands, modify branch protection, rename branches, delete repository artifacts, deploy the platform, create release tags, open beta traffic, process live learner traffic, launch billing, or authorise new KG scope.

The only handoff authority created by this slice is that PRD-1 may become the next controlled implementation stream after PRD-0.10 evidence is captured and merged.

---

## Closure checks

The closure evidence must prove:

- PRD-0.0 through PRD-0.9 verifiers are valid.
- PRD-0.9 repository hygiene audit is closed.
- The production-readiness register records `last_recorded_item: PRD-0.10`.
- The production-readiness register records `next_authorised_item: PRD-1`.
- PRD-1 is recorded as the next controlled workstream.
- PRD-2 through PRD-11 remain blocked until their own gates.
- Production release, deployment, release tags, public beta, live learner traffic, billing, payment processing, and new KG slices remain unauthorised.

---

## Validation

Before evidence capture:

```bash
PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd010_prd0_closure_evidence_handoff.py --authority-only --json
```

Expected authority state: `authority_valid: true`, `valid: false`.

After evidence capture:

```bash
PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd010_prd0_closure_evidence_handoff.py --json
```

Expected final state: `authority_valid: true`, `valid: true`, `next_authorised_item: PRD-1`.
"""

PLAN_TEXT = """# PRD-0.10 Closure Evidence and PRD-1 Handoff Plan

## Goal

Close PRD-0 by recording a verifiable terminal evidence bundle and handing the production-readiness stream to PRD-1.

## Steps

1. Apply PRD-0.10 authority files from clean `master`.
2. Run `py_compile`, focused PRD-0.10 tests, and the authority verifier.
3. Commit and merge the authority branch.
4. From merged `master`, capture PRD-0 closure evidence.
5. Run the final PRD-0.10 verifier.
6. Commit and merge the evidence branch.
7. Treat PRD-1 — Required CI and Release Gate Convergence as the next authorised workstream.

## Non-goals

- No PRD-1 implementation is performed in PRD-0.10.
- No production release is authorised.
- No deployment is authorised.
- No release tag is authorised.
- No public beta or live learner traffic is authorised.
- No billing or live payment processing is authorised.
- No repository cleanup or history rewrite is authorised.
- No new KG slice is authorised.

## Expected terminal register state

```json
{
  "last_recorded_item": "PRD-0.10",
  "next_authorised_item": "PRD-1"
}
```
"""

SCHEMA_TEXT = """# PRD-0.10 Closure Evidence and Handoff Schema

The captured snapshot is stored at:

`docs/roadmap/production_readiness/prd0_closure_evidence_handoff.json`

Required top-level fields:

| Field | Meaning |
|---|---|
| `schema_version` | Must be `prd0-closure-evidence-handoff/v1`. |
| `prd_id` | Must be `PRD-0.10`. |
| `captured_at` | UTC timestamp for evidence capture. |
| `prd0_verifier_results` | Verifier results for PRD-0.0 through PRD-0.9. |
| `all_prd0_predecessors_valid` | True only when PRD-0.0 through PRD-0.9 are valid. |
| `register_summary` | Register state before/after closure handoff. |
| `authority_boundaries` | Closed release/beta/billing/live/KG boundaries. |
| `handoff` | PRD-1 handoff status and explicit no-implementation boundary. |

Required closed boundaries:

- `production_release_authorised: false`
- `deployment_authorised: false`
- `release_tag_authorised: false`
- `public_beta_authorised: false`
- `live_learner_traffic_authorised: false`
- `billing_launch_authorised: false`
- `live_payment_processing_authorised: false`
- `new_kg_slice_authorised: false`
- `prd1_implementation_authorised: false`

Required handoff fields:

- `prd0_closed: true`
- `next_authorised_item: PRD-1`
- `prd1_handoff_authorised: true`
- `no_prd1_implementation_performed: true`
"""

CHECKLIST_TEXT = """# PRD-0 Closure Handoff Checklist

- [ ] PRD-0.0 verifier valid.
- [ ] PRD-0.1 verifier valid.
- [ ] PRD-0.2 verifier valid.
- [ ] PRD-0.3 verifier valid.
- [ ] PRD-0.4 verifier valid.
- [ ] PRD-0.5 verifier valid.
- [ ] PRD-0.6 verifier valid.
- [ ] PRD-0.7 verifier valid.
- [ ] PRD-0.8 verifier valid.
- [ ] PRD-0.9 verifier valid.
- [ ] PRD-0.10 authority verifier valid.
- [ ] Evidence captured from merged `master`.
- [ ] Register records PRD-0.10 as the last recorded item.
- [ ] Register records PRD-1 as the next authorised item.
- [ ] PRD-1 handoff is documented without PRD-1 implementation changes.
- [ ] Production release, deployment, release tags, beta, live learner traffic, billing, payments, and new KG scope remain unauthorised.
"""

HANDOFF_TEXT = """# PRD-0 to PRD-1 Handoff

**From:** PRD-0 — Post-Closure Current-State Authority Refresh  
**To:** PRD-1 — Required CI and Release Gate Convergence  
**Canonical trunk:** `master`

## Handoff statement

After PRD-0.10 evidence capture, PRD-0 is closed and PRD-1 becomes the next authorised controlled workstream.

This handoff does not itself implement PRD-1. PRD-1 must still proceed as its own authority/evidence stream.

## PRD-1 objective

Make CI production-reliable by converging required checks, release workflow semantics, branch protection evidence, and OpenAPI artifact authority.

## Inputs from PRD-0

- Production-readiness register exists and records PRD-0.0 through PRD-0.10.
- Canonical current-state documentation is refreshed.
- Historical/stale reports are quarantined.
- Documentation housekeeping ratchets are refreshed.
- Test/dependency bootstrap baseline is recorded.
- Test failure and collection stabilisation register exists.
- Workflow command hygiene and CI inventory is recorded.
- OpenAPI/generated artifact canonicalisation is recorded.
- Branch/release naming reconciliation is recorded.
- Repository hygiene and generated/local artifact audit is recorded.

## Boundaries carried into PRD-1

PRD-1 may work on CI/release gate convergence only. It does not authorise production release, deployment, release tag creation, public beta, live learner traffic, billing launch, live payment processing, or new KG scope.
"""

INITIAL_RECORD = {
    "prd_id": PRD_ID,
    "stream_id": "PRD-PRODUCTION-READINESS",
    "status": "prd0_closure_handoff_authority_recorded",
    "prd009_repository_hygiene_generated_local_artifact_audit_valid": True,
    "all_prd0_predecessors_valid": True,
    "prd0_closure_evidence_recorded": False,
    "prd0_handoff_to_prd1_recorded": False,
    "prd0_sequence_complete": False,
    "prd0_closure_checklist_refreshed": True,
    "prd1_handoff_document_refreshed": True,
    "next_authorised_item": "PRD-0.10",
    "prd1_handoff_authorised": False,
    "no_prd1_implementation_performed": True,
    **TRUE_BOUNDARIES,
    **FALSE_BOUNDARIES,
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def apply(root: Path = Path("."), write_files: bool = False) -> dict:
    files = {
        PRD_DOC: PRD_DOC_TEXT,
        PLAN: PLAN_TEXT,
        SCHEMA_DOC: SCHEMA_TEXT,
        CHECKLIST: CHECKLIST_TEXT,
        HANDOFF_DOC: HANDOFF_TEXT,
    }
    changed = []
    for rel, text in files.items():
        path = root / rel
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            changed.append(str(rel))
        if write_files:
            write(path, text)
    record_path = root / RECORD
    if not record_path.exists():
        changed.append(str(RECORD))
        if write_files:
            write_json(record_path, INITIAL_RECORD)
    elif write_files:
        # Preserve captured records, but backfill missing authority keys.
        try:
            existing = json.loads(record_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
        updated = {**INITIAL_RECORD, **existing}
        write_json(record_path, updated)
    return {
        "prd_id": PRD_ID,
        "changed_files": changed,
        "prd0_closure_checklist_refreshed": True,
        "prd1_handoff_document_refreshed": True,
        "prd1_handoff_authorised": False,
        "no_prd1_implementation_performed": True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "live_learner_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "new_kg_slice_authorised": False,
        "prd1_implementation_authorised": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = apply(Path(args.root), write_files=args.write)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.10 closure handoff authority checked. changed={len(result['changed_files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
