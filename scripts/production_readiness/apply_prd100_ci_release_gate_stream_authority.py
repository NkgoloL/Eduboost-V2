
#!/usr/bin/env python3
"""Apply PRD-1.0 CI/release-gate stream authority files.

This script establishes the PRD-1 authority/register layer after PRD-0.10.
It does not canonicalise workflows, enforce required checks, alter branch
protection, create release tags, deploy, open beta/live learner traffic, launch
billing, process payments, or implement PRD-2 runtime KG work.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PRD_ID = "PRD-1.0"
STREAM_ID = "PRD-1-CI-RELEASE-GATE-CONVERGENCE"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD1_REGISTER = ROOT / "prd1_ci_release_gate_register.json"
PRD_DOC = ROOT / "prd_100_ci_release_gate_stream_authority.md"
PLAN = ROOT / "prd1_ci_release_gate_stream_authority_plan.md"
SCHEMA_DOC = ROOT / "prd1_ci_release_gate_register.schema.md"
SEQUENCE_DOC = ROOT / "prd1_ci_release_gate_sequence.md"
RECORD = ROOT / "prd_100_ci_release_gate_stream_authority_record.json"
ENGINEERING_DOC = Path("docs/engineering/prd1_ci_release_gate_convergence.md")

TRUE_BOUNDARIES = {
    "runtime_kg_implementation_claimed": True,
    "runtime_kg_authority_switch_authorised": True,
    "authority_switch_executed": True,
}
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
    "prd2_implementation_authorised": False,
}
NO_CHANGE_FLAGS = {
    "ci_workflow_changes_performed": False,
    "required_checks_enforced": False,
    "release_gate_enforced": False,
    "branch_protection_modified": False,
    "workflow_canonicalisation_performed": False,
    "openapi_reconciliation_performed": False,
}

PRD1_ITEMS = [
    ("PRD-1.0", "CI/release-gate stream authority and register"),
    ("PRD-1.1", "CI inventory authority"),
    ("PRD-1.2", "Required check classification"),
    ("PRD-1.3", "Workflow canonicalisation"),
    ("PRD-1.4", "Release gate definition"),
    ("PRD-1.5", "CI convergence evidence"),
    ("PRD-1.6", "Release readiness register"),
    ("PRD-1.7", "Authority reconciliation"),
    ("PRD-1.8", "Final evidence capture"),
    ("PRD-1.9", "Controlled handoff to PRD-2 Runtime KG Integration and Persistence"),
]

PRD_DOC_TEXT = """# PRD-1.0 — CI/Release-Gate Stream Authority and Register

**Stream:** PRD-1 — Required CI and Release Gate Convergence  
**Status:** Authority slice; evidence capture required for closure  
**Owner:** Nkgolo Lebelo  
**Canonical trunk:** `master`

---

## Purpose

PRD-1.0 establishes the authority layer for PRD-1 after the PRD-0.10 handoff.

It creates the PRD-1 sub-slice register, records the PRD-1 execution sequence, and confirms that PRD-1 is limited to CI and release-gate convergence until later PRDs authorise product runtime, beta, billing, or production release work.

---

## PRD-1 goal

Make CI production-reliable by converging required checks, release workflow semantics, branch protection evidence, and release-gate authority.

---

## PRD-1 controlled sequence

1. PRD-1.0 — CI/release-gate stream authority and register.
2. PRD-1.1 — CI inventory authority.
3. PRD-1.2 — Required check classification.
4. PRD-1.3 — Workflow canonicalisation.
5. PRD-1.4 — Release gate definition.
6. PRD-1.5 — CI convergence evidence.
7. PRD-1.6 — Release readiness register.
8. PRD-1.7 — Authority reconciliation.
9. PRD-1.8 — Final evidence capture.
10. PRD-1.9 — Controlled handoff to PRD-2 Runtime KG Integration and Persistence.

---

## Explicit boundary

PRD-1.0 does not modify CI workflows, enforce branch protection, standardise pytest calls, remove stale workflows, reconcile OpenAPI files, define release gates, capture CI convergence, create release tags, deploy, open beta/live learner traffic, launch billing, process live payments, or implement runtime KG work.

Those actions are reserved for later PRD-1.x slices or later major PRDs.

---

## Closure condition

Before evidence capture, the verifier must report `authority_valid: true` and `valid: false`.

After evidence capture, the verifier must report `authority_valid: true`, `valid: true`, and `next_authorised_item: PRD-1.1`.
"""

PLAN_TEXT = """# PRD-1.0 CI/Release-Gate Stream Authority Plan

## Goal

Establish PRD-1 as the active controlled workstream after PRD-0.10, without performing CI or release-gate implementation.

## Steps

1. Apply PRD-1.0 authority files from clean `master` after PRD-0.10 closure.
2. Run `py_compile`, focused PRD-1.0 tests, and the authority verifier.
3. Commit and merge the authority branch.
4. From merged `master`, capture PRD-1.0 evidence.
5. Run the final PRD-1.0 verifier.
6. Commit and merge the evidence branch.
7. Treat PRD-1.1 — CI Inventory Authority as the next authorised slice.

## Non-goals

- No CI workflow canonicalisation.
- No required-check enforcement.
- No branch protection change.
- No release gate enforcement.
- No release tag or deployment.
- No public beta, live learner traffic, billing, or live payment processing.
- No PRD-2 runtime KG implementation.

## Expected terminal register state

```json
{
  "last_recorded_item": "PRD-1.0",
  "next_authorised_item": "PRD-1.1"
}
```
"""

SCHEMA_TEXT = """# PRD-1 CI/Release-Gate Register Schema

The PRD-1 register is stored at:

`docs/roadmap/production_readiness/prd1_ci_release_gate_register.json`

Required top-level fields:

| Field | Meaning |
|---|---|
| `schema_version` | Must be `prd1-ci-release-gate-register/v1`. |
| `stream_id` | Must be `PRD-1-CI-RELEASE-GATE-CONVERGENCE`. |
| `parent_stream_id` | Must be `PRD-PRODUCTION-READINESS`. |
| `goal` | Required CI and release gate convergence goal. |
| `last_recorded_item` | Last recorded PRD-1.x slice. |
| `next_authorised_item` | Next authorised PRD-1.x slice. |
| `prd1_sequence` | PRD-1.0 through PRD-1.9 authority sequence. |
| `authority_boundaries` | Explicitly closed release/beta/billing/live/KG boundaries. |
| `implementation_boundaries` | Explicit no-change status for PRD-1.0. |

PRD-1.0 terminal state requires:

- `last_recorded_item: PRD-1.0`
- `next_authorised_item: PRD-1.1`
- `PRD-1.0` sequence entry status `recorded`
- `PRD-1.1` sequence entry authorised `true`
- production release, deployment, release tags, beta, live learner traffic, billing, payments, and PRD-2 implementation all unauthorised
"""

SEQUENCE_TEXT = """# PRD-1 Required CI and Release Gate Convergence Sequence

| Slice | Name | Purpose |
|---|---|---|
| PRD-1.0 | CI/release-gate stream authority and register | Establish PRD-1 authority and sub-slice register. |
| PRD-1.1 | CI inventory authority | Inventory all CI, workflow, release, check, branch-protection, and OpenAPI command sources. |
| PRD-1.2 | Required check classification | Classify checks as required, advisory, stale, legacy, release-only, or blocked. |
| PRD-1.3 | Workflow canonicalisation | Standardise pytest invocation, master/main semantics, release workflow ambiguity, and OpenAPI artifact references. |
| PRD-1.4 | Release gate definition | Define authoritative release gate checks and release-blocking rules. |
| PRD-1.5 | CI convergence evidence | Capture evidence that required checks are stable/green or explicitly blocked. |
| PRD-1.6 | Release readiness register | Record release readiness state without authorising release. |
| PRD-1.7 | Authority reconciliation | Reconcile PRD-1 records, CI state, release-gate state, and PRD-0 handoff state. |
| PRD-1.8 | Final evidence capture | Capture final PRD-1 evidence bundle. |
| PRD-1.9 | Controlled handoff to PRD-2 | Close PRD-1 and authorise PRD-2 handoff without implementing runtime KG. |

PRD-1 ends only with a controlled handoff to PRD-2. It does not authorise production deployment, public beta, live learner traffic, billing, or payment processing.
"""

ENGINEERING_TEXT = """# PRD-1 CI and Release Gate Convergence

PRD-1 exists to make CI production-reliable after PRD-0 closed the current-state authority refresh.

## Carried-in facts from PRD-0

- Canonical trunk: `master`.
- Legacy `main` references are compatibility/historical unless explicitly reconciled.
- `release/**` branches are reserved naming patterns, not release authority.
- Generated/local artifact cleanup remains audit-only unless explicitly authorised.
- Production release, deployment, beta, live learner traffic, billing, live payment processing, and new KG scope remain blocked.

## PRD-1 implementation boundary

PRD-1 may only converge CI and release-gate authority. Runtime KG implementation is reserved for PRD-2. Learner/parent journey hardening is reserved for PRD-3. Content quality readiness is reserved for PRD-4. POPIA live data operations are reserved for PRD-5. Security assurance is reserved for PRD-6. SRE readiness is reserved for PRD-7. Scale/cost execution is reserved for PRD-8. Billing is reserved for PRD-9. Controlled beta is reserved for PRD-10. Production release/deployment is reserved for PRD-11.
"""

WORKFLOW_TEXT = """name: PRD-1.0 CI Release Gate Stream Authority

on:
  pull_request:
    paths:
      - '.github/workflows/prd100-ci-release-gate-stream-authority.yml'
      - 'docs/engineering/prd1_ci_release_gate_convergence.md'
      - 'docs/roadmap/production_readiness/**'
      - 'scripts/production_readiness/*prd100*'
      - 'scripts/roadmap_reconciliation/*prd100*'
      - 'tests/unit/roadmap_reconciliation/test_prd100_ci_release_gate_stream_authority.py'
      - 'Makefile'
  workflow_dispatch:

jobs:
  prd100-authority:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Compile PRD-1.0 scripts
        run: |
          python3 -m py_compile \
            scripts/production_readiness/apply_prd100_ci_release_gate_stream_authority.py \
            scripts/production_readiness/audit_prd100_ci_release_gate_stream_authority.py \
            scripts/roadmap_reconciliation/capture_prd100_ci_release_gate_stream_authority_evidence.py \
            scripts/roadmap_reconciliation/verify_prd100_ci_release_gate_stream_authority.py
      - name: Focused PRD-1.0 tests
        run: |
          PYTHONPATH=. python3 -m pytest -q \
            tests/unit/roadmap_reconciliation/test_prd100_ci_release_gate_stream_authority.py \
            --no-cov
      - name: Verify PRD-1.0 authority
        run: |
          PYTHONPATH=. python3 \
            scripts/roadmap_reconciliation/verify_prd100_ci_release_gate_stream_authority.py \
            --authority-only --json
"""


def prd1_sequence_initial():
    items = []
    for prd_id, name in PRD1_ITEMS:
        if prd_id == PRD_ID:
            items.append({"prd_id": prd_id, "name": name, "authorised": True, "status": "authority_pending"})
        else:
            items.append({"prd_id": prd_id, "name": name, "authorised": False, "status": "blocked"})
    return items


def initial_prd1_register():
    return {
        "schema_version": "prd1-ci-release-gate-register/v1",
        "stream_id": STREAM_ID,
        "parent_stream_id": "PRD-PRODUCTION-READINESS",
        "goal": "make CI production-reliable",
        "canonical_trunk_branch": "master",
        "last_recorded_item": None,
        "next_authorised_item": PRD_ID,
        "status": "prd1_stream_authority_ready",
        "authorised_by_prd0_10": True,
        "prd1_sequence": prd1_sequence_initial(),
        "authority_boundaries": {**TRUE_BOUNDARIES, **FALSE_BOUNDARIES},
        "implementation_boundaries": {**NO_CHANGE_FLAGS},
    }

INITIAL_RECORD = {
    "prd_id": PRD_ID,
    "stream_id": STREAM_ID,
    "status": "prd1_stream_authority_recorded",
    "prd010_prd0_closure_evidence_handoff_valid": True,
    "prd1_register_created": True,
    "prd1_sequence_registered": True,
    "prd1_stream_authority_recorded": False,
    "prd1_authority_evidence_recorded": False,
    "next_authorised_item": PRD_ID,
    "prd1_1_authorised": False,
    "no_ci_workflow_changes_performed": True,
    "no_required_check_enforcement_performed": True,
    "no_release_gate_enforcement_performed": True,
    "no_branch_protection_change_performed": True,
    "no_openapi_reconciliation_performed": True,
    "no_prd2_implementation_performed": True,
    **TRUE_BOUNDARIES,
    **FALSE_BOUNDARIES,
    **NO_CHANGE_FLAGS,
}

MAKEFILE_BLOCK = """
# PRD-1.0 CI/release-gate stream authority and register
.PHONY: prd100-ci-release-gate-stream-authority-audit
prd100-ci-release-gate-stream-authority-audit:
	$(PYTHON) scripts/production_readiness/audit_prd100_ci_release_gate_stream_authority.py --json

.PHONY: prd100-ci-release-gate-stream-authority-check
prd100-ci-release-gate-stream-authority-check:
	$(PYTHON) -m py_compile scripts/production_readiness/apply_prd100_ci_release_gate_stream_authority.py scripts/production_readiness/audit_prd100_ci_release_gate_stream_authority.py scripts/roadmap_reconciliation/capture_prd100_ci_release_gate_stream_authority_evidence.py scripts/roadmap_reconciliation/verify_prd100_ci_release_gate_stream_authority.py
	PYTHONPATH=. $(PYTHON) -m pytest -q tests/unit/roadmap_reconciliation/test_prd100_ci_release_gate_stream_authority.py --no-cov
	PYTHONPATH=. $(PYTHON) scripts/roadmap_reconciliation/verify_prd100_ci_release_gate_stream_authority.py --authority-only --json

.PHONY: prd100-ci-release-gate-stream-authority-capture
prd100-ci-release-gate-stream-authority-capture:
	PYTHONPATH=. $(PYTHON) scripts/roadmap_reconciliation/capture_prd100_ci_release_gate_stream_authority_evidence.py --claim-prd100-ci-release-gate-stream-authority --prd-owner "$${PRD_OWNER:-Nkgolo Lebelo}" --target-branch "$${TARGET_BRANCH:-master}" --require-valid --json
# End PRD-1.0 CI/release-gate stream authority and register
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_makefile(root: Path) -> bool:
    path = root / "Makefile"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if "prd100-ci-release-gate-stream-authority-check" in text:
        return False
    if text and not text.endswith("\n"):
        text += "\n"
    write(path, text + MAKEFILE_BLOCK)
    return True


def apply(root: Path = Path("."), write_files: bool = False) -> dict:
    files = {
        PRD_DOC: PRD_DOC_TEXT,
        PLAN: PLAN_TEXT,
        SCHEMA_DOC: SCHEMA_TEXT,
        SEQUENCE_DOC: SEQUENCE_TEXT,
        ENGINEERING_DOC: ENGINEERING_TEXT,
        Path(".github/workflows/prd100-ci-release-gate-stream-authority.yml"): WORKFLOW_TEXT,
    }
    changed = []
    for rel, text in files.items():
        path = root / rel
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            changed.append(str(rel))
        if write_files:
            write(path, text)

    reg_path = root / PRD1_REGISTER
    if not reg_path.exists():
        changed.append(str(PRD1_REGISTER))
        if write_files:
            write_json(reg_path, initial_prd1_register())
    elif write_files:
        try:
            existing = json.loads(reg_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
        merged = {**initial_prd1_register(), **existing}
        merged.setdefault("authority_boundaries", {}).update({k: v for k, v in {**TRUE_BOUNDARIES, **FALSE_BOUNDARIES}.items() if k not in merged.get("authority_boundaries", {})})
        merged.setdefault("implementation_boundaries", {}).update({k: v for k, v in NO_CHANGE_FLAGS.items() if k not in merged.get("implementation_boundaries", {})})
        write_json(reg_path, merged)

    record_path = root / RECORD
    if not record_path.exists():
        changed.append(str(RECORD))
        if write_files:
            write_json(record_path, INITIAL_RECORD)
    elif write_files:
        try:
            existing = json.loads(record_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
        write_json(record_path, {**INITIAL_RECORD, **existing})

    if write_files:
        if ensure_makefile(root):
            changed.append("Makefile")
    else:
        mf = root / "Makefile"
        if mf.exists() and "prd100-ci-release-gate-stream-authority-check" not in mf.read_text(encoding="utf-8"):
            changed.append("Makefile")

    return {
        "prd_id": PRD_ID,
        "stream_id": STREAM_ID,
        "changed_files": sorted(set(changed)),
        "prd1_register_created": True,
        "prd1_sequence_registered": True,
        "next_authorised_item": PRD_ID,
        "no_ci_workflow_changes_performed": True,
        "no_release_gate_enforcement_performed": True,
        "no_prd2_implementation_performed": True,
        **TRUE_BOUNDARIES,
        **FALSE_BOUNDARIES,
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
        print(f"PRD-1.0 authority checked. changed={len(result['changed_files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
