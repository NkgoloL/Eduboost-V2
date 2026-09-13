---
title: "Technical Audit Remediation Phase 02J — Tracked Topic-Map Text-Extract Provenance"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'architecture']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Technical Audit Remediation Phase 02J — Tracked Topic-Map Text-Extract Provenance

## Purpose

Close the final backend-fast topic-map provenance failure by ensuring the reviewed text-extract manifest is part of the tracked repository state, not only a local generated artifact.

## Root cause

`data/content_factory/*` is ignored globally, and `.gitignore` only allowed `scopes.json` and `coverage_targets.json` back into source control. Phase 02I verification could pass on a local machine that had `data/content_factory/source_text_extracts_manifest.json`, while a clean checkout or repo zip omitted that file and caused the topic-map worklist to fall back to the PDF source hash.

## Changes

- Allowlist `data/content_factory/source_text_extracts_manifest.json` in `.gitignore`.
- Track the reviewed Senior Phase Mathematics text-extract provenance record.
- Add a verifier that checks both provenance correctness and clean-checkout trackability.
- Add focused regression tests for the exact failure.

## Evidence boundary

This phase produces focused remediation evidence only. Backend-fast candidate evidence remains blocked until `make test-fast` exits 0.

## KG boundary

This change preserves future knowledge-graph provenance hooks as metadata only. It does not introduce runtime knowledge-graph implementation.
