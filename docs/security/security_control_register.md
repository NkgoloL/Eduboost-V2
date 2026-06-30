---
title: "Security Control Register"
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

# Security Control Register

## Required Control Fields

- control ID
- security domain
- control name
- control description
- implementation status
- evidence path
- owner
- production blocking flag

## Required Production-Blocking Controls

- secure session defaults
- object-level authorization
- PII and secret redaction
- SBOM and dependency review
- security header policy
- vulnerability scan gate
- secret scan gate
- incident response runbook

## Boundary

This register records security controls. It does not modify application behavior by itself.
