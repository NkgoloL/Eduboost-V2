---
title: "Consent Rejection Audit"
status: archived
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: null
evidence_command: null
code_anchors: [docs/security/README.md, app/security]
archived_at: '2026-09-23'
---
# Consent Rejection Audit
> [!NOTE]
> **Status: ARCHIVED — 2026-09-23**
> Historical milestone evidence, review audit, or point-in-time record; retained for audit lineage.



## Purpose

When active consent is missing or expired, learner-data processing must be
rejected and auditable.

## Contract

`ConsentService.require_active_consent` must preserve evidence for:

- `consent.access_rejected`
- `ConsentRequiredError`
- `ConsentExpiredError`
- audit append fallback
- Fourth Estate rejected-outcome semantics

## Command

```bash
make popia-consent-rejection-audit-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_consent_rejection_audit_check.py -q --no-cov
```
