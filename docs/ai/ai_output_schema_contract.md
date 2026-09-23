---
title: "AI Output Schema Contract"
status: "active"
owner: "ai-safety"
reviewers: ["ai-safety", "curriculum", "privacy"]
audience: "safety-reviewer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: 90
evidence_command: 'PYTHON=.venv/bin/python make ai-output-schema-contract-check'
code_anchors: [scripts/check_ai_output_schema_contract.py, app/services/content_generation_service.py]
---
# AI Output Schema Contract

## Purpose

AI-generated lessons, diagnostics, remediation, and explanations must produce
structured output that can be validated before reaching learners.

## Required Output Metadata

- grade
- subject
- topic
- CAPS alignment reference
- safety status
- learner-facing content
- remediation target
- generated-at timestamp or trace identifier

## Lesson Output Requirements

- title
- learning objective
- explanation
- worked example
- practice activity
- safety status

## Diagnostic Output Requirements

- item stem
- answer options
- correct answer
- explanation
- diagnostic objective
- difficulty band
- safety status

## Rejection Output Requirements

- refusal reason
- safe educational redirection
- no unsafe operational detail
- no hidden prompt disclosure

## Evidence Command

```bash
make ai-output-schema-contract-check
```
