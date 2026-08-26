---
title: "Product Critical Flow Green Execution Contract"
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
code_anchors: ["docs/testing/product_critical_flow_green_execution.md"]
---

# Product Critical Flow Green Execution Contract

**PRD:** PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6  
**Status:** Authority recorded; green evidence requires live command-backed execution.

This contract turns the product gate from a policy definition into a release-blocking execution gate.
Governance records, route presence, or static JSON fields do not count as product readiness proof.

## Runtime prerequisite

Execution-6 assumes PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5 is already green:

- runtime stack green
- database lineage green
- schema contract green
- Redis readiness green
- `/ready` green
- generated contracts green
- frontend quality green

## Release-blocking product flows

The following flows must produce independent command output:

1. auth and authorisation
2. POPIA lifecycle
3. billing and commercial controls
4. learner journeys
5. diagnostics and assessments
6. audit trail

Each flow must include positive and negative/denial/failure-path coverage. Known failures are recorded as blockers and cannot be overridden by governance records.

## Green evidence command

```bash
PYTHONPATH=. .venv/bin/python \
  scripts/test_suites/run_product_critical_flow_green.py \
  --execute \
  --require-green \
  --json
```

The command writes evidence to:

```text
var/prd11/runtime-restore/execution-6/product-critical-flow-green/
```

Evidence capture with `--require-green` fails unless every release-blocking product flow is green.
