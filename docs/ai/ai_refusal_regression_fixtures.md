---
title: "AI Refusal Regression Fixtures"
status: "active"
owner: "ai-safety"
reviewers: "[ai-safety, curriculum, privacy]"
audience: "safety-reviewer"
source_of_truth: "false"
supersedes: "[]"
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: "60"
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/services, docs/ai]"
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
