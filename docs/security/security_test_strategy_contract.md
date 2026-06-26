---
title: "Security Test Strategy Contract"
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

# Security Test Strategy Contract

## Purpose

This contract defines required security tests for pull request, staging, and production gates.

## Required Security Tests

- SAST
- dependency scan
- secret scan
- container scan
- DAST
- API fuzzing
- config audit
- threat model review

## Required Gate Rules

- SAST must run for pull requests
- dependency scan must run for pull requests
- secret scan must run for pull requests
- production security tests must also gate staging
- production security tests must block release
- security test artifacts must be retained under controlled paths

## Boundary

This contract records security-test readiness. It does not execute security tests.
