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

## Controlled status language

Use explicit evidence-bound qualifiers instead of blanket delivery claims. The following forms are acceptable only when tied to scope, date, command output, and evidence path:

- implementation present
- targeted checks passed
- CI evidence attached
- staging evidence attached
- external approval attached
- verified against the listed scope
- not yet verified for the requested claim
- blocked by missing evidence

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
