---
title: "Release — ARQ Consent Job Repair Report"
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
# ARQ Consent Job Repair Report

Generated at: `2026-05-17T22:05:40Z`

**Status:** implemented

- Consent reminder job uses `AsyncSessionLocal`.
- Consent reminder job constructs `ConsentRepository(session)`.
- Consent reminder job constructs `ConsentService` with explicit dependencies.
- FastAPI BackgroundTasks policy docstring updated.
