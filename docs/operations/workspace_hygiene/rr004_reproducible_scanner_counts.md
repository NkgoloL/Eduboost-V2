---
title: RR-004 Reproducible Scanner Counts
status: active
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# RR-004 Reproducible Scanner Counts

RR-004 requires reproducible scanner counts so workspace hygiene can be checked without relying on ad-hoc shell output.

## Required scanner fields

The scanner output includes:

```text
tracked_file_count
tracked_docs_count
tracked_scripts_count
tracked_tests_count
tracked_generated_or_evidence_count
ignored_artifact_candidate_count
extension_counts
top_level_counts
```

## Reproducibility rules

- Prefer `git ls-files` for tracked-file counts.
- Use `git status --ignored --short` for ignored artifact candidate counts.
- Sort count dictionaries before writing JSON.
- Keep cleanup evidence dry-run only.
- Do not include local secrets, `.env` values, database dumps, or learner data in evidence.

## Boundary

These counts are repository hygiene evidence only. They do not authorise release, deployment, public beta, expanded learner traffic, or runtime KG implementation.
