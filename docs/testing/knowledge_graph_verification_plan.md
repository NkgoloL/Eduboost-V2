---
title: "Knowledge Graph Verification Plan"
status: active
owner: quality
reviewers: [architecture, product, privacy, curriculum, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make kg000-formal-kg-roadmap-approval-check
code_anchors: []
---

# Knowledge Graph Verification Plan

## Purpose

This plan defines the verification gates needed before the knowledge graph learning-state model becomes authoritative.

## Verification layers

### Documentation verifier

Confirms formal pivot docs exist and indexes reference them, and optionally that their content matches the reviewed package (see `--manifest` below).

**Scope note:** this verifier checks presence and cross-referencing only. It does not check that a mapping is curriculum-correct, that a schema migration matches this data model, or that generated content is actually grounded. A pass here means "the governance paperwork is in place," not "the pivot is implemented correctly" — see KG-R13 in the risk register. Report it as such at phase-gate reviews.

Command:

```bash
python3 scripts/phase02r/verify_phase02r_knowledge_graph_pivot_docs.py --root .
```

Optional package-integrity check (confirms the docs in the target repo are byte-identical to the reviewed package they were copied from, useful immediately after applying, before you delete the extracted package):

```bash
python3 scripts/phase02r/verify_phase02r_knowledge_graph_pivot_docs.py --root /path/to/Eduboost-V2 --manifest /path/to/extracted-package/MANIFEST.json
```

### Graph schema verifier

Future verifier. Confirms migrations create graph tables, indexes, constraints, and review-status rules.

### CAPS graph verifier

Future verifier. Confirms CAPS graph nodes and edges have stable keys, source references, source checksums, allowed node/edge types, valid node references, no duplicate keys, and approved status before production use.

### Target graph verifier

Future verifier. Confirms target graph references only approved CAPS nodes, includes mastery/confidence thresholds, is scoped by grade/subject/term or beta scope, and has no orphaned expectations.

### Learner graph verifier

Future verifier. Confirms learner state cannot update without evidence event, keeps valid mastery/confidence ranges, preserves update provenance, and supports export and erasure fixtures.

### Generation grounding verifier

Future verifier. Confirms lessons and assessments include graph node references, source evidence, target known gaps, validate prerequisite assumptions, and generate expected evidence events.

### API/OpenAPI verifier

Future verifier. Confirms graph API routes are included in OpenAPI and client contracts.

### POPIA verifier

Future verifier. Confirms learner graph and evidence event data are included in data-rights workflows.

## Minimum acceptance before authority switch

The graph model cannot become authoritative until documentation verifier, migration graph verifier, schema integrity verifier, CAPS graph verifier, target graph verifier, learner graph verifier, generation grounding verifier, POPIA export/erasure fixtures, OpenAPI/client contract check, full backend fast gate, frontend gates, and release evidence are green.

## Test fixture strategy

Required fixtures: approved Grade 4 Mathematics CAPS node set, target graph for beta scope, learner with strong mastery, learner with prerequisite blocker, learner with misconception marker, learner with insufficient evidence, diagnostic event sequence, IRT update sequence, lesson completion event, failed assessment event, and POPIA export/erasure fixture.
