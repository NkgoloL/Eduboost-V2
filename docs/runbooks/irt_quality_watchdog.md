---
title: "IRT Quality Watchdog Runbook"
status: "active-runbook"
owner: "operations"
reviewers: ["operations", "engineering", "release-management"]
audience: "operator"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[docs/runbooks, docs/operations]"
---

# IRT Quality Watchdog Runbook

## Scheduled operation

The ARQ worker runs `run_irt_quality_watchdog` nightly at 02:00 UTC. The job is idempotent per calendar date and records an `irt_calibration_runs` row plus append-only item events.

## Manual dry run

Use the protected admin API:

```http
POST /api/v2/admin/irt-quality/runs
{"dry_run": true, "idempotency_key": "manual-review-YYYYMMDD"}
```

A dry run records a run summary but does not change item state or create rewrite artifacts.

## Incident response

### Unexpected quarantine spike

1. Pause the nightly worker schedule or disable its deployment revision.
2. Query the latest run summary and event reasons.
3. Confirm the response sample and session-rest-score inputs.
4. Do not restore learner eligibility through direct SQL.
5. Use the manual override API with an attributable reason only after statistical/content review.
6. Record the incident and re-run in dry-run mode.

### Failed calibration job

1. Inspect durable job status and the `irt_calibration_runs.error` payload.
2. Correct the dependency or data issue.
3. Retry with the same idempotency key only if the failed run contains no committed item events; otherwise use a new key and document the superseding run.

### Rewrite created

The rewrite artifact must remain `pending_review`, `publication_eligible=false`, and complete the Phase 3 educator-consensus workflow. Never directly promote it.

## Safe rollback

Application code may be rolled back, but calibration events are evidence and must not be deleted. Prefer a forward fix for the Phase 4 migration. Confirm that learner selection still excludes all quarantined/retired items after rollback.
