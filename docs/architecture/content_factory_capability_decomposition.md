---
title: Content Factory Capability Decomposition
status: active
owner: architecture
reviewers: [engineering, content-factory]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-09-03
review_interval_days: 60
evidence_command: make docs-housekeeping-check
code_anchors: [docs/architecture/content_factory_capability_decomposition.md]
---

# Content Factory Capability Decomposition (TSR-6.2, TSR-6.6)

## Architectural Purpose
The Content Factory is decomposed into clear capability layers to avoid monolithic control structures and ensure strict transaction boundaries.

## Capability Domains
1. **Curriculum Scope & Target Definition:**
   - Managed by `ContentScopeRegistry` and `content_scopes` / `content_coverage_targets`.
2. **Generation Control Plane:**
   - Executed via `ContentGenerationRun` and `ContentGenerationTask` with budget reservations.
3. **Artifact Staging & Verification:**
   - Managed via `ContentStagingArtifact` and `ContentStagingVerificationRun` with hash validation.
4. **Pedagogical Review & Consensus:**
   - Maker-checker review workflows using `ContentReviewDecision` and `ContentReviewAssignment`.
5. **Production Promotion:**
   - Promotion ledger governed by `ContentPromotionEvent` and `ContentProductionArtifact`.
