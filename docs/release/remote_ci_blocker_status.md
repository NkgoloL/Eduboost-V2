---
title: "Release — Remote CI Blocker Status"
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
# Remote CI Blocker Status

**Status:** pending external GitHub Actions evidence

The repository is not beta-ready until the current fork has at least one green CI run and that run URL is archived in `docs/release/ci_evidence.md`.
