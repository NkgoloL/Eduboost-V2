---
title: "AI Lesson Safety Baseline"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'architecture']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# AI Lesson Safety Baseline

PR-006 establishes the minimum runtime contract for AI-generated lesson content.

## Safety gates

AI lesson output must pass:

1. strict Pydantic structured-output validation;
2. answer-key presence checks;
3. safety-pattern screening;
4. CAPS topic/reference validation;
5. PII redaction before learner context reaches the LLM prompt;
6. content-quality scoring.

## Structured lesson metadata

Lesson payloads now include:

- CAPS reference;
- CAPS topic/subtopic;
- lesson variant;
- language level;
- safety classification;
- alignment confidence;
- quality score;
- trust label.

## Deterministic provider

`LLM_PROVIDER=mock` enables deterministic offline generation for tests and contract validation. It should not be used as a production-quality tutor; it exists to keep safety and OpenAPI tests stable without external providers.

## Remaining limitations

The baseline does not yet provide a full symbolic arithmetic solver, human review queue UI, or complete CAPS coverage. Low-confidence or high-impact content should still be treated as requiring review before public claims are made.
