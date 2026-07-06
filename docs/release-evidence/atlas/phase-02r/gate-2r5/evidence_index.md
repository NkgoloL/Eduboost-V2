---
title: Phase 2R Gate 2R.5 Evidence Index
status: evidence-record
owner: evidence-custodian
reviewers: [evidence-custodian, release-management, documentation-governance]
audience: evidence-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release-evidence, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Phase 2R Gate 2R.5 Evidence Index

**Generated:** 2026-06-22T20:06:41Z
**Status:** Candidate verification passed — human approval pending
**Source commit:** `a31be31d7323f675b83430dc775084abc44f58ce`
**Environment:** see `raw/environment.txt`

| Evidence ID / claim | Artifact |
|---|---|
| Gate 2R.5 preflight authorised from Gate 2R.4 | `raw/preflight.txt` |
| Gate 2R.5 integrated verifier | `raw/verify_phase02r.txt`, `raw/verify_phase02r_gate2r5.json` |
| Approved semantic corpus manifest is deterministic and hashable | `raw/semantic_corpus_manifest.json` |
| Retrieval projection contains only active approved corpus membership | `raw/retrieval_projection.json` |
| Active binding/corpus/binding-epoch retrieval controls reject stale or mixed reads | `raw/retrieval_validation.json` |
| PostgreSQL/Alembic corpus-table readiness disclosed | `raw/verify_phase02r_gate2r5_postgres.txt` |
| Focused Gate 2R.5 tests | `raw/focused_tests.txt` |
| Raw evidence checksums | `raw/SHA256SUMS.txt` |
