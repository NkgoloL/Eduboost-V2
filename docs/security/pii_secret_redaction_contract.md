---
title: "PII and Secret Redaction Contract"
status: active
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, app/security]
---

# PII and Secret Redaction Contract

## Required Redaction Controls

- raw passwords are prohibited in logs
- raw API keys are prohibited in logs
- raw tokens are prohibited in logs
- private keys are prohibited in logs
- learner names are minimized
- emails are redacted where not required
- phone numbers are redacted where not required
- raw AI prompts are excluded from telemetry
- raw provider payloads are excluded from telemetry

## Boundary

This contract records redaction expectations. It does not process live telemetry.
