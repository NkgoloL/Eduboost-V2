---
title: "AI Output Fixtures"
status: "active"
owner: "ai-safety"
reviewers: ["ai-safety", "curriculum", "privacy"]
audience: "safety-reviewer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/services, docs/ai]"
---

# AI Output Fixtures

## Purpose

Fixture-based AI output validation checks structured lesson, diagnostic, and
refusal examples without making live model calls.

## Fixtures

- `tests/fixtures/ai/safe_lesson_output.json`
- `tests/fixtures/ai/safe_diagnostic_output.json`
- `tests/fixtures/ai/refusal_output.json`

## Required Fixture Types

- lesson
- diagnostic
- refusal

## Safety Requirements

- safe outputs must contain `safety_status`
- lesson outputs must include learner-facing educational content
- diagnostic outputs must include answer keys and explanations
- refusal outputs must include safe educational redirection
- refusal outputs must not disclose hidden prompts
