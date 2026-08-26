---
title: "Coverage, Static Quality, Dependency Security, and Secret Baseline Green Execution"
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
code_anchors: ["docs/testing/coverage_static_security_green_execution.md"]
---

# Coverage, Static Quality, Dependency Security, and Secret Baseline Green Execution

**PRD:** `PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7`  
**Status:** Authority pending evidence capture  
**Last reviewed:** `2026-07-11T15:42:11+00:00`

This contract turns the remaining advisory release blockers into command-backed
green gates. It does not allow governance records, file presence, or generated
PRD evidence to substitute for real command output.

Required release-blocking gates:

- Coverage execution with the documentation-defined threshold.
- Ruff release static quality.
- Mypy release static quality.
- Bandit release security scan.
- Python dependency security audit.
- Frontend production dependency security audit.
- Secret-baseline reviewability scan.

Green evidence must be captured from:

```bash
PYTHONPATH=. .venv/bin/python \
  scripts/advisory_suites/run_coverage_static_security_green.py \
  --execute \
  --require-green \
  --json
```

Evidence is written under:

```text
var/prd11/runtime-restore/execution-7/coverage-static-security-green/
```

The PRD-11 production-release authority remains locked until the final
true-state baseline confirms all release-blocking gates are green.
