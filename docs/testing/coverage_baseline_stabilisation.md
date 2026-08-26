---
title: "Execution-7 Coverage Baseline Stabilisation"
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
code_anchors: ["docs/testing/coverage_baseline_stabilisation.md"]
---

# Execution-7 Coverage Baseline Stabilisation

## Purpose

The first independent `coverage_execution` run remained active but exceeded the original 900-second bound. This remediation replaces the single opaque `make test-coverage` process with deterministic and independently bounded execution.

This work remains inside `PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7`. It does not capture green Execution-7 evidence, mark Execution-7 complete, or authorise Execution-8.

## Execution model

The stabilised runner:

1. Discovers unit and integration test files deterministically.
2. Records collection output, collection duration, and collected-test counts separately for each suite.
3. Preserves eight deterministic parent unit shards, splits them into bounded leaf shards, and adaptively bisects only leaves that time out.
4. Runs each unit leaf in a disposable Git worktree so tracked mutations are attributable without dirtying the operator branch.
5. Balances integration files into deterministic shards and runs them sequentially to avoid uncontrolled shared database or Redis contention.
6. Writes each shard's exact command, timestamps, timeout state, exit code, normalized failure classification, remaining failure count, stdout, and stderr.
7. Stores coverage data and reports only under `var/prd11/runtime-restore/execution-7/coverage-baseline-stabilisation/`.
8. Discards timed-out attempt coverage data and combines coverage only after all final unit and integration shards complete.
9. Produces JSON, XML, HTML, and terminal threshold reports only from a complete shard baseline.
10. Compares tracked Git worktree state before and after execution and blocks green status if tests mutate tracked files.

The default release threshold remains 70 percent. The existing marker policy remains:

```text
not governance and not slow and not llm and not e2e
```

## Plan and authority verification

```bash
PYTHONPATH=. .venv/bin/python \
  scripts/coverage_suites/run_coverage_baseline_stabilisation.py \
  --json

PYTHONPATH=. .venv/bin/python \
  scripts/coverage_suites/verify_coverage_baseline_stabilisation.py \
  --json
```

Plan mode does not run tests. It records deterministic file counts and shard membership.

## Real remediation execution

Run from a fresh branch based on merged `master`:

```bash
PYTHONPATH=. .venv/bin/python \
  scripts/coverage_suites/run_coverage_baseline_stabilisation.py \
  --execute \
  --require-green \
  --json
```

Equivalent Make target:

```bash
make coverage-baseline-stabilisation
```

Useful tuning flags are available for diagnosis without changing the contract defaults:

```text
--unit-shards
--integration-shards
--workers
--collection-timeout-seconds
--unit-timeout-seconds
--integration-timeout-seconds
--output-dir
```

Any non-default run must retain the same marker expression, threshold, isolated artifact path, independent command evidence, and clean-worktree requirement before it can support the canonical release gate.

## Expected artifacts

```text
var/prd11/runtime-restore/execution-7/coverage-baseline-stabilisation/
  plan.json
  summary.json
  collection/
  shards/
  reports/
  coverage-data/
  coverage.json
  coverage.xml
  html/
```

## Result interpretation

A timeout now identifies the exact collection phase or adaptive unit leaf. A normal test failure identifies the affected shard and preserves its complete output. Coverage report generation and the 70 percent threshold are evaluated only after every final shard completes, preventing partial coverage from being presented as a final threshold result. Tracked generated-file mutations are listed explicitly and prevent a green result.

The Execution-7 evidence capture remains prohibited until this coverage gate and every other release-blocking Execution-7 gate are green from merged `master`.
