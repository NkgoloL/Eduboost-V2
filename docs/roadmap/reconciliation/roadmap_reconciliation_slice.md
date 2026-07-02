# Roadmap Reconciliation Slice

**Status:** authority harness / pending evidence capture  
**Owner:** roadmap-owner  
**Purpose:** reconcile actual merged evidence against canonical roadmap and TODO sources before introducing any new work.

## Why this slice exists

The recent runtime-readiness and beta-governance work created several evidence-gated records after the original roadmap was written. Some of those records are valuable, but the numbering and status language can make it look as though the canonical roadmap has many more phases than it originally did.

This slice corrects that by establishing one rule:

> **No new workstream may be introduced until outstanding tasks from canonical roadmap and TODO sources have been reconciled into the Outstanding Work Register.**

## Scope

This slice does not implement product features. It creates a source-controlled reconciliation layer that:

1. inventories canonical roadmap and TODO sources;
2. classifies later Phase 18–21 records as auxiliary beta-operations governance unless explicitly promoted later;
3. creates an outstanding-work register grouped by canonical roadmap area;
4. records the current boundary for production release, public beta, deployment, live learner traffic, learner migration, and runtime KG work;
5. adds capture and verification scripts so the reconciliation claim is evidence-backed.

## Canonical sources

The initial canonical source set is recorded in:

```text
docs/roadmap/reconciliation/canonical_roadmap_sources.json
```

## Reconciled outstanding work

The initial outstanding-work register is recorded in:

```text
docs/roadmap/reconciliation/outstanding_work_register.md
```

## Classification of Phase 18–21

The later Phase 18–21 records are useful evidence controls, but they are not treated as new canonical roadmap phases by this slice. They are classified as beta-operations governance records in:

```text
docs/roadmap/reconciliation/phase_18_to_21_governance_classification.md
```

## Freeze rule

New roadmap phases, workstreams, and implementation bundles are frozen until outstanding canonical roadmap items are triaged and selected from the reconciled register.

The freeze is documented in:

```text
docs/roadmap/reconciliation/roadmap_new_work_freeze.md
```

## Evidence capture

After this harness lands on `master`, run:

```bash
python3 scripts/roadmap_reconciliation/capture_roadmap_reconciliation_evidence.py \
  --claim-roadmap-reconciliation \
  --reconciliation-owner "Nkgolo Lebelo" \
  --target-branch master \
  --require-valid \
  --json

python3 scripts/roadmap_reconciliation/verify_roadmap_reconciliation.py --json
```

## Boundary

This slice does **not** authorise:

- production release;
- public beta;
- production deployment;
- release tagging;
- new feature work outside the reconciled register;
- runtime KG implementation;
- expansion beyond currently approved controlled-beta governance.
