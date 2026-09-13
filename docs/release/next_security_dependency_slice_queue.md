---
title: "Release — Next Security and Dependency Slice Queue"
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
# Next Security and Dependency Slice Queue

**Status:** queued after auth router boundary closure

## Candidate next batch

`code_751_780`: dependency pinning, JWT key rotation, and remaining auth service extraction.

## Scope candidates

1. Pin Python dependency lock files using the project virtual environment.
2. Add JWT `kid` support and current/previous key rotation contract.
3. Move remaining auth router repository usage into a canonical AuthService.
4. Remove auth router import-linter transition allowances.
5. Add regression tests for refresh-token authorization scope after key rotation.
