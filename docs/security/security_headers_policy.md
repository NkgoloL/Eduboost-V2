---
title: "Security Headers Policy"
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

# Security Headers Policy

## Required Headers

- Strict-Transport-Security
- Content-Security-Policy
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy

## Required Rules

- HSTS is required for production
- Content-Security-Policy is required for production
- X-Content-Type-Options must use nosniff
- X-Frame-Options must prevent clickjacking
- Referrer-Policy must minimize leakage

## Boundary

This policy records security header expectations. It does not configure the runtime server.
