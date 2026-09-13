---
title: "Release — Next Execution Queue After TX-001 / code_1391_1430"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Next Execution Queue After TX-001 / code_1391_1430

## Recommended next batch

`TX-001B / code_1431_1470` — targeted rollback proof for one high-risk multi-write flow.

## Preferred scope

Start with POPIA lifecycle transition + audit write because it is both compliance-critical and transaction-sensitive.

Candidate acceptance:

1. Use a transactional test DB fixture.
2. Force audit write failure after consent transition attempt.
3. Assert consent transition is rolled back.
4. Force consent write failure before audit attempt.
5. Assert no audit orphan is written.
6. Record evidence without claiming all domains are atomic.
