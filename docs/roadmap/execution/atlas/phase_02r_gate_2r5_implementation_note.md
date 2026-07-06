---
title: Phase 02R Gate 2R.5 Implementation Note — Semantic Corpus and Real-Source Retrieval
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Phase 02R Gate 2R.5 Implementation Note — Semantic Corpus and Real-Source Retrieval

**Status:** implementation package only; not an approval record
**Gate:** 2R.5
**Boundary:** Gate 2R.6+ not started

## Implemented controls

Gate 2R.5 introduces the controlled semantic-corpus and retrieval-projection layer:

- complete activation key: `curriculum_code + grade + subject_code + delivery_language + tenant_scope`;
- deterministic manifest hashing for frozen corpus membership;
- eligibility checks for rights, source status, extraction review, mapping review, language authority status, quality score, Tier 1 support and security warnings;
- rejection of synthetic fixtures and machine/generated text as official authority;
- retrieval projection built only from manifest membership;
- active binding validation by `activation_key`, `corpus_version_id`, `binding_epoch`, and `manifest_sha256`;
- versioned cache key contract that includes binding epoch;
- staging activation/rollback planning with transactional-outbox events;
- candidate evidence collection for semantic corpus, retrieval projection and retrieval validation.

## Deliberate exclusions

This implementation does not approve Gate 2R.5, authorise Gate 2R.6, execute a live database migration, wire production generation/tutor/study-plan/learner-facing behaviour, or publish/activate production retrieval endpoints.

## Verification commands

```bash
bash scripts/preflight_phase02r.sh --gate 2R.5
bash scripts/verify_phase02r.sh --gate 2R.5 --mode implementation
bash scripts/verify_phase02r_gate2r5_postgres.sh
python scripts/curriculum/build_phase02r_gate2r5_semantic_corpus.py --json
python scripts/curriculum/export_phase02r_gate2r5_retrieval_projection.py --json
python scripts/curriculum/validate_phase02r_gate2r5_retrieval.py --json
python -m pytest -q tests/unit/phase02r/test_gate2r5_semantic_corpus.py --no-cov
```

## Evidence command

```bash
bash scripts/collect_phase02r_evidence.sh --gate 2R.5
```

The evidence collector emits candidate evidence only and must be followed by a separate evidence commit, separate approval manifest commit, and separate transition commit before Gate 2R.6 may begin.
