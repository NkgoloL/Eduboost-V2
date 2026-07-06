---
title: "Knowledge Graph Learning Model Brief"
status: active
owner: product
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

# Product Brief: Knowledge Graph Learning Model

## Summary

EduBoost is pivoting from a feature-centric adaptive-learning platform to a CAPS-grounded knowledge graph learning-state platform.

The product promise becomes:

> EduBoost knows what CAPS expects, estimates what the learner currently knows, explains the gap, and selects evidence-backed interventions to move the learner toward the expected state.

## Why this change is needed

The current feature set is valuable but can become fragmented: diagnostics measure ability, IRT calibrates difficulty, lessons teach, practice reinforces, study plans schedule, gamification motivates, parent portal reports, and CAPS ingestion grounds content.

Without a shared state model, each feature can produce its own idea of progress. That causes inconsistent recommendations, weaker explainability, and harder governance.

The knowledge graph model gives all features a single educational truth structure: CAPS graph as curriculum truth, target graph as expected state, learner graph as current state, evidence events as why the state is believed, and interventions as how EduBoost changes state.

## Product outcomes

### Learner

- Receives activities based on actual gaps and prerequisites.
- Gets remediation before being pushed into harder content.
- Sees progress in meaningful skills, not just completed lessons.

### Parent / guardian

- Understands where the learner is relative to expected grade/term state.
- Sees evidence-backed progress and next steps.
- Can review reports and privacy/consent history.

### Educator / curriculum reviewer

- Reviews CAPS mappings and generated content against explicit graph nodes.
- Can inspect why a lesson or assessment exists.
- Can identify curriculum coverage gaps.

### Engineering

- Gains a single model for diagnostics, lessons, study plans, reports, and tutor decisions.
- Reduces duplicate mastery logic.
- Improves testability and release evidence.

## Product rule

Every adaptive-learning feature must answer this question:

> Which graph state does this feature observe, explain, or change?

If the answer is unclear, the feature is not ready for core architecture implementation.

## Initial beta scope

The first implementation remains Grade 4 Mathematics, aligned to the existing beta and Phase 02R focus. The pivot must not expand beta scope before Grade 4 Mathematics is proven.
