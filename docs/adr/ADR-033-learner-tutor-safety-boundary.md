---
title: "ADR-033 — Learner Tutor Safety and Context Boundary"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-033 — Learner Tutor Safety and Context Boundary

**Status:** Proposed for Phase 5 approval  
**Date:** 2026-06-15

## Decision

The learner tutor is a lesson-scoped, authenticated support tool. It is not a general-purpose chatbot and it does not publish or alter curriculum content.

The tutor:

- requires an active-consent, learner-owned lesson;
- uses a bounded lesson excerpt plus non-identifying learning-gap topics;
- redacts recognised personal information before provider calls and persistence;
- rejects prompt-injection and high-risk requests before provider calls;
- validates and redacts provider output before learner delivery;
- persists only redacted text and a hash of the original learner question;
- uses explicit, non-deceptive fallback messages;
- creates educator/safeguarding escalations for unsafe or low-quality interactions;
- is protected by endpoint rate limits and token budgets;
- supports cancellation and client disconnect without claiming a response completed;
- does not use tutor conversations as training data without a separate approved governance decision.

## Consequences

The tutor may refuse legitimate questions that resemble prompt injection or high-risk requests. Educator escalation and periodic sampled-quality review are required. Provider streaming may be represented as controlled server-sent chunks after a validated response so unsafe partial output is never shown.
