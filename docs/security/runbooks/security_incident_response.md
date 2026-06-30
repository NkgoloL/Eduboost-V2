---
title: "Security Incident Response Runbook"
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

# Security Incident Response Runbook

## Triage

- assign security owner
- classify incident severity
- preserve evidence
- identify affected service and data class

## Containment

- disable affected credential
- isolate affected service
- block malicious source where appropriate
- pause affected integration where appropriate

## Eradication

- remove malicious change
- rotate exposed secrets
- patch vulnerable dependency
- verify clean artifact

## Recovery

- restore trusted artifact
- verify smoke tests
- monitor security metrics
- confirm service integrity

## Notification

- notify release owner
- notify privacy owner where applicable
- notify support owner where applicable
- follow legal/privacy notification workflow where applicable

## Boundary

This runbook records incident response expectations. It does not execute incident response automatically.
