---
title: "Flake Policy and Quarantine Register"
status: "active"
owner: "quality"
reviewers: "[quality, engineering, release-management]"
audience: "quality-reviewer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[tests, pytest.ini, Makefile]"
---

# Flake Policy and Quarantine Register

## 1. Zero-Concealment Flake Policy
1. **No Silent Retries**: Retries in CI must never conceal first-attempt test failures. If a test is flaky, it must be reported.
2. **Quarantine SLA**: Any quarantined test must have:
   - A dedicated tracking issue.
   - A designated maintainer owner.
   - An expiration date (maximum 14 days).
   - Documented reproduction steps.
3. **Release Gate Rule**: No release candidate may be cut with active quarantined tests in core authorization, payment-disabled paths, or learner mastery modules.

## 2. Active Quarantine Register
Current status: **0 Quarantined Tests (Clean)**.

| Test ID | Module | Reason | Owner | Quarantined At | Expiration Date |
|---|---|---|---|---|---|
| *None* | — | — | — | — | — |
