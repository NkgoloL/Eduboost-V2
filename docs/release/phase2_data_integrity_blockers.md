---
title: "Release — Phase 2 Data Integrity Blockers"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Phase 2 Data Integrity Blockers

**Status:** queued after architecture boundary enforcement

## Candidate follow-on batches

1. Diagnostics item/mastery data integrity:
   - protect theta/state updates from invalid item payloads
   - enforce attempt ownership and assessment ownership boundaries
2. Repository/service duplicate cleanup:
   - classify duplicate domain services
   - remove only call-site-proven legacy code
3. Worker/job runtime repair:
   - validate ARQ job construction
   - validate consent/audit worker payload shapes
4. Operational evidence:
   - real staging smoke
   - real disposable DB proof
   - backup/restore/rollback drills

## Non-goals

Do not delete tables, audit history, consent history, or active runtime facades without evidence.
