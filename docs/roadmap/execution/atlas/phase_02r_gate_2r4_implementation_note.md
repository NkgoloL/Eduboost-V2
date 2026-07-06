---
title: Phase 02R Gate 2R.4 Implementation Note
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

# Phase 02R Gate 2R.4 Implementation Note

**Gate:** 2R.4 — Curriculum knowledge graph and reviewed mappings  
**Status:** Implementation asset, not approval evidence  
**Boundary:** No corpus activation, no production retrieval projection, no embeddings, no generation/tutor behaviour change, no learner-facing change.

## Implemented controls

- Curriculum node and immutable node-version model.
- Reviewed curriculum edge versions: `prerequisite_of`, `sequence_before`, `supports`, `assesses`, `same_concept_as`, `translation_of`.
- Source-to-curriculum mapping versions with source chunk/page/section provenance.
- Review-state machine: `proposed`, `in_review`, `approved`, `rejected`, `needs_revision`, `superseded`, `withdrawn`.
- Tier 1 support readiness validation for approved CAPS requirements.
- Maker-checker enforcement with explicit self-review exception metadata when unavoidable.
- Append-only mapping review events with per-item approval trace requirements.
- Language authority labels: `official_source`, `approved_human_translation`, `machine_translation_draft`, `generated_learner_explanation`.
- Deterministic graph export and validation scripts for evidence hashing.

## Verification

Run:

```bash
bash scripts/preflight_phase02r.sh --gate 2R.4
bash scripts/verify_phase02r.sh --gate 2R.4
bash scripts/verify_phase02r_gate2r4_postgres.sh
python scripts/curriculum/validate_phase02r_gate2r4_graph.py --json
python scripts/curriculum/export_phase02r_curriculum_graph.py --json
```

For live PostgreSQL closure proof, run the PostgreSQL verifier with a controlled `DATABASE_URL` and `PHASE02R_REQUIRE_LIVE_DB=1`.

## Approval boundary

This note does not approve Gate 2R.4 and does not authorise Gate 2R.5. Approval must wait for committed passing evidence and a separate approval manifest.
