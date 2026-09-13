---
title: "Reference — Learning Engines"
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
# Learning Engines

The bounded-context modules below drive the adaptive logic behind diagnostics,
archetype onboarding, and lesson orchestration.

## Diagnostics / IRT
::: app.modules.diagnostics.irt_engine
::: app.modules.diagnostics.service

## Consent
::: app.modules.consent.service

## Learner Archetypes
::: app.modules.learners.ether_service

## Lessons
::: app.modules.lessons.llm_gateway

## Auth
::: app.modules.auth.service
