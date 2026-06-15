# ADR-032 — Governed Curriculum Expansion and Training Dataset Manifests

**Status:** Accepted for Phase 7 implementation  
**Date:** 2026-06-15

## Context

EduBoost needs to expand curriculum coverage and may eventually train focused adapters. Coverage pressure must not bypass source grounding, educator review, publication, safety, licensing, privacy, or durable budget controls. Existing training scripts can consume arbitrary JSONL and therefore require a governed handoff.

## Decision

1. Coverage snapshots and expansion plans are durable and deterministic.
2. Expansion plans never publish or train directly.
3. Only eligible published artifacts enter training manifests.
4. Dataset entries are append-only and approved manifests are immutable.
5. Every record and dataset has a reproducible SHA-256 identity.
6. Training readiness requires an approved manifest.
7. CI validates training configuration through dry runs; actual training and deployment are separate decisions.
8. Machine language checks do not replace qualified human language review.
9. Learner, guardian, reviewer-comment, tutor-message, response, consent, billing, and audit data are excluded.

## Consequences

- Dataset volume may be lower than desired.
- Curriculum and language reviewers remain on the critical path.
- Training runs can be reproduced and audited.
- A trained adapter cannot be interpreted as approved for learner traffic.
