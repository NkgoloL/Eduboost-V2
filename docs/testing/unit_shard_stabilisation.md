---
title: "Execution-7 Unit-Shard Stabilisation"
status: "active"
owner: "quality"
reviewers: ["quality", "engineering"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-08-26"
review_interval_days: 60
evidence_command: "make docs-housekeeping-check"
code_anchors: ["docs/testing/unit_shard_stabilisation.md"]
---

# Execution-7 Unit-Shard Stabilisation

## Purpose

The first deterministic coverage run completed both integration shards, but six of eight large unit shards timed out and the remaining two exposed 30 concrete failures. The partial coverage result was therefore not a valid final threshold measurement.

This remediation retains the eight-parent unit-shard authority model and replaces each large unit execution with adaptive leaf execution. It remains inside `PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7`; it does not capture green evidence, mark Execution-7 complete, or authorise Execution-8.

## Execution model

The unit stabiliser:

1. Recreates the canonical eight-parent unit shard plan deterministically.
2. Splits each selected parent into two initial leaf shards.
3. Runs each leaf with verbose pytest progress, bounded execution, slow-test reporting, and exact file membership.
4. Executes every leaf in a disposable detached Git worktree so generated or mutated tracked files can be attributed without dirtying the operator branch.
5. Removes coverage data from timed-out attempts.
6. Bisects only timed-out leaves, up to the controlled maximum depth.
7. Preserves completed failing leaves as concrete failure evidence rather than hiding them through further splitting.
8. Records failed and errored node IDs, the last active test line, slowest tests, exact mutation files, and a mutation patch per leaf.
9. Allows coverage combination and threshold evaluation only after every final unit and integration shard completes.

The marker policy and 70 percent threshold remain unchanged.

## Verify authority and plan

```bash
PYTHONPATH=. .venv/bin/python \
  scripts/coverage_suites/verify_unit_shard_stabilisation.py \
  --json

PYTHONPATH=. .venv/bin/python \
  scripts/coverage_suites/run_unit_shard_stabilisation.py \
  --json
```

The default plan creates 16 initial leaf shards: two beneath each of the eight canonical parent unit shards.

## Targeted remediation

A single parent can be diagnosed independently:

```bash
PYTHONPATH=. .venv/bin/python \
  scripts/coverage_suites/run_unit_shard_stabilisation.py \
  --parent-shard-id unit-01-of-08 \
  --execute \
  --json
```

Multiple parent IDs may be repeated or supplied as a comma-separated value.

## Canonical coverage rerun

The existing canonical command now invokes the adaptive unit stabiliser automatically:

```bash
export DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres

PYTHONPATH=. .venv/bin/python \
  scripts/coverage_suites/run_coverage_baseline_stabilisation.py \
  --execute \
  --require-green \
  --json
```

Equivalent target:

```bash
make coverage-baseline-stabilisation
```

## Artifacts

```text
var/prd11/runtime-restore/execution-7/unit-shard-stabilisation/
  plan.json
  summary.json
  leaves/
  mutations/
  test-artifacts/
  coverage-data/
```

When invoked through the canonical coverage runner, unit artifacts are nested under:

```text
var/prd11/runtime-restore/execution-7/coverage-baseline-stabilisation/
  unit-shard-stabilisation/
```

## Interpretation

A final timed-out leaf means the unit baseline remains incomplete. Coverage reports are intentionally skipped in that state, and the canonical blocker is `coverage_incomplete_shards`, not a misleading report-generation or threshold failure.

Completed test failures remain release-blocking and include exact node IDs. Tracked mutations are attributed to the leaf that caused them, while the source worktree remains clean because the leaf runs in a disposable worktree.
