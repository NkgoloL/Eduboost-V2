---
title: "Frontend Accessibility Contract"
status: "active"
owner: "frontend"
reviewers: ["frontend", "product", "privacy"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/frontend, docs/frontend/README.md]"
---

# Frontend Accessibility Contract

## Purpose

Cluster G frontend journeys must be accessible to learners and parents using
keyboard navigation, screen readers, clear focus states, and age-appropriate
error messaging.

## Required Accessibility Rules

- every interactive control has an accessible name
- forms expose visible labels or ARIA labels
- page sections use semantic landmarks where possible
- keyboard navigation reaches primary learner and parent actions
- focus indicators are visible
- error messages are announced or associated with fields
- status/loading states are understandable without color alone
- consent and authorization denial states use plain-language copy
- learner-facing copy remains age-appropriate
- parent trust and progress surfaces avoid data overexposure

## Required Journey Coverage

- learner onboarding
- learner dashboard
- diagnostic start and submit
- lesson view
- progress/mastery feedback
- parent dashboard
- consent status/trust dashboard
- authorization and consent denial states

## Command

```bash
make frontend-accessibility-contract-check
```
