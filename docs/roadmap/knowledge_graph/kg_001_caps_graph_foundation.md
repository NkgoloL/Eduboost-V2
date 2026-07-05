---
title: "KG-1 CAPS Graph Foundation"
status: active
owner: knowledge-graph
reviewers: [architecture, curriculum, engineering, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make kg001-caps-graph-foundation-check
code_anchors: []
---

# KG-1 — CAPS Graph Foundation

## Purpose

KG-1 creates the first source-grounded CAPS graph read model for the Grade 4 Mathematics beta scope. It converts the approved CAPS topic map into a deterministic graph artifact with curriculum, grade, subject, term, topic, subtopic, assessment-statement, and misconception nodes.

## Scope

Included:

- deterministic CAPS graph artifact generation;
- source checksum and source reference preservation for every node and edge;
- graph schema, loader contract, review manifest, and runtime boundary;
- verification/capture scripts and evidence path.

Excluded:

- database schema migration;
- learner graph implementation;
- target graph generation;
- runtime KG authority switch;
- learner-facing model changes;
- production release, deployment, release tagging, and public beta authority.

## Exit criteria

- KG-0 is valid.
- Grade 4 Mathematics CAPS graph artifact is generated.
- Every graph node and edge has source provenance.
- Duplicate node keys and orphan edges are absent.
- Runtime KG boundary remains false.

## Next slice

After KG-1 evidence lands, the next KG slice is **KG-2 — Target graph generation**.
