---
title: "KG-2 Target Graph Generation"
status: active
owner: knowledge-graph
reviewers: [architecture, product, privacy, curriculum, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make kg002-target-graph-generation-check
code_anchors: []
---


# KG-2 — Target Graph Generation

## Purpose

KG-2 derives the expected Grade 4 Mathematics learner state from the approved
KG-1 CAPS graph artifact. The output is a source-grounded target graph read
model that can later be compared against learner graph shadow state.

## Scope

- Grade 4 Mathematics only.
- Uses only approved KG-1 CAPS graph nodes.
- Generates target states for topic, subtopic, and assessment-statement nodes.
- Records required mastery, confidence, priority, and pacing windows.
- Preserves runtime KG authority boundaries.

## Non-goals

- No database migration.
- No learner graph implementation.
- No learner-facing model change.
- No runtime KG authority switch.
- No production release or public beta authority.

## Exit criteria

- Target graph artifact generated.
- Target graph references approved CAPS nodes only.
- Required mastery and confidence thresholds are present.
- Priority weighting and pacing windows are present.
- No duplicate target keys.
- No orphan target edges.
