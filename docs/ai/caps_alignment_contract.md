---
title: "CAPS Alignment Contract"
status: active
owner: ai-safety
reviewers: [ai-safety, curriculum, privacy]
audience: safety-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [app/services, docs/ai]
---

# CAPS Alignment Contract

## Purpose

EduBoost AI and diagnostic generation must remain aligned to the South African
CAPS curriculum and must expose evidence that generated learning material is
bounded by grade, subject, topic, and learner state.

## Required Alignment Fields

- grade
- subject
- topic
- CAPS strand or skill
- difficulty band
- learner mastery state
- diagnostic objective
- remediation objective

## AI Generation Boundaries

- generated lessons must reference learner grade and subject
- generated diagnostics must be objective-bound
- generated remediation must map to observed learner gaps
- outputs must avoid unsupported curriculum claims
- model fallback must preserve CAPS-aligned prompts

## Evidence Commands

```bash
make caps-alignment-contract-check
```

## Release Evidence

Attach CAPS alignment evidence before staging release when AI or diagnostic
generation logic changes.
