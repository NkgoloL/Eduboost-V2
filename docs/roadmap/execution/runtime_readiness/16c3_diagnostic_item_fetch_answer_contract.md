---
title: "Runtime Readiness — Phase 16C-3 — Diagnostic Item Fetch and Answer Submission Contract Repair"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'product']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Phase 16C-3 — Diagnostic Item Fetch and Answer Submission Contract Repair

**Status:** repair harness installed; evidence unclaimed.

## Purpose

Make the backend-backed seeded diagnostic route fetch deterministic item-bank
data and submit stable answer keys (`A`/`B`/`C`/`D`) without claiming the full
Phase 16 seeded E2E gate.

## Repairs

- Seed deterministic Grade 3 diagnostic items during non-production
  dev-session bootstrap.
- Serialise canonical diagnostic item-bank records into frontend subject
  codes and stable option payloads.
- Fix the Next backend proxy so GET responses forward their body.
- Keep the UI displaying answer labels while submitting answer keys.
- Allow diagnostic submission to score canonical item-bank answers.

## Boundary

This slice is diagnostic runtime-contract repair only. It does not claim
Phase 16 seeded E2E evidence, production release, deployment, release
tagging, live learner traffic, or runtime KG implementation.
