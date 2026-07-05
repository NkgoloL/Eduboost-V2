---
title: "Logging and Tracing Contract"
status: "active"
owner: "operations"
reviewers: ["operations", "security", "backend"]
audience: "operator"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/api_v2.py, docs/observability]"
---

# Logging and Tracing Contract

## Purpose

This contract defines structured logging and distributed tracing requirements.

## Required Log Fields

- request_id
- trace_id
- span_id
- user_scope
- service
- environment
- route or operation
- status or outcome
- duration where applicable

## Prohibited Log Fields

- password
- raw prompt
- raw AI output
- raw provider payload
- card number
- learner name where not required
- email address before redaction
- phone number before redaction
- South African ID number before redaction

## Required Trace Controls

- API request span
- database query span
- LLM provider request span
- billing webhook span
- notification provider span
- error sampling
- request ID propagation
- trace ID propagation
- PII-safe attributes only

## Boundary

This contract records logging and tracing readiness. It does not configure a live collector or export production traces.
