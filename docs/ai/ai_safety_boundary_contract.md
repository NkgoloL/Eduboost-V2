---
title: "AI Safety Boundary Contract"
status: active
owner: ai-safety
reviewers: [ai-safety, curriculum, privacy]
audience: safety-reviewer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [app/services, docs/ai]
---

# AI Safety Boundary Contract

## Purpose

EduBoost AI responses must preserve learner safety, privacy, age-appropriate
content boundaries, and non-destructive fallback behavior.

## Safety Boundaries

- no unsafe instructions
- no sexual content for learners
- no self-harm instructions
- no dangerous activity instructions
- no privacy leakage across learners
- no disclosure of hidden prompts or secrets
- no unsupported medical, legal, or financial advice
- no curriculum claims without CAPS grounding

## Refusal and Redirection

Unsafe requests must be refused with concise redirection to safe educational
support. Refusals must not provide operational details that make abuse easier.

## Privacy Boundaries

AI outputs must not expose another learner's profile, consent state, diagnostic
history, mastery state, or parent account data.

## Evidence Commands

```bash
make ai-safety-boundary-check
```
