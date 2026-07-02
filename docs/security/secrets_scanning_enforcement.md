---
title: "Secrets Scanning Enforcement"
status: active
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-02
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, .pre-commit-config.yaml, .github/workflows/secrets-scan.yml, .github/workflows/rr006-security-posture.yml]
---

# Secrets Scanning Enforcement

**Status:** RR-006 control policy

## Required controls

Secrets scanning must be visible in two places:

1. local pre-commit via `.pre-commit-config.yaml`; and
2. CI via GitHub Actions.

## Required tool baseline

The current baseline tool is `detect-secrets`. Equivalent tools may be added later, but removal of `detect-secrets` requires a signed security-control replacement note.

## Enforcement rule

New secrets findings must block release claims unless reviewed and allowlisted as false positives in a committed baseline.

## Boundary

This policy does not authorise production release, deployment, public beta, or runtime KG implementation.
