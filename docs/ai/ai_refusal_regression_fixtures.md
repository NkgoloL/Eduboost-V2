---
title: "AI Refusal Regression Fixtures"
status: active
owner: "ai-safety"
reviewers: ["ai-safety", "curriculum", "privacy"]
audience: "safety-reviewer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: 90
evidence_command: make docs-housekeeping-check
code_anchors: "[app/services, docs/ai/README.md]"
---
# AI Refusal Regression Fixtures

## Purpose

Refusal fixtures validate that unsafe, privacy-invasive, or hidden-prompt
requests produce safe refusal records without live model calls.

## Fixture Categories

- unsafe instruction
- privacy leakage
- hidden prompt disclosure

## Required Refusal Fields

- case ID
- category
- safety status
- refusal reason
- safe educational redirection
- no unsafe operational detail
- no hidden prompt disclosure

## Command

```bash
make ai-refusal-fixture-check
```
