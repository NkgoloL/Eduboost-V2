---
title: Documentation Claim Discipline Policy
status: active
owner: documentation-governance
reviewers: [release-management, engineering, security, privacy]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-06-22
review_interval_days: 30
evidence_command: python3 scripts/maintenance/check_doc_truth_claims.py --root . --canonical-only
code_anchors: [scripts/maintenance/check_doc_truth_claims.py]
---

# Documentation Claim Discipline Policy

EduBoost documents must avoid unsupported broad claims.

## Controlled terms

The following terms are allowed only when they are bounded by scope, date, and evidence:

- production-ready
- release-ready
- launch approved
- fully complete
- all tests pass
- green baseline
- compliant
- secure
- complete

## Required evidence language

Use bounded wording:

- `As of YYYY-MM-DD, command X passed in environment Y.`
- `This is candidate evidence, not release approval.`
- `This document is historical and not current source of truth.`
- `This readiness statement is limited to the checks listed below.`

Do not use unbounded wording:

- `The platform is production ready.`
- `All checks pass.`
- `POPIA is complete.`
- `Security is done.`

## Release claims

Release claims must link to:

- a release decision record;
- an evidence index;
- exact commands run;
- exact date/time;
- known limitations.
