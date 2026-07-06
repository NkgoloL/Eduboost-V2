---
title: Production support model
status: active
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Production support model

## Channels

- Support email: `support@eduboost.co.za`
- Security disclosure: `security@eduboost.co.za`
- Privacy requests: `privacy@eduboost.co.za`

## Severity levels

| Severity | Example | Target response |
|---|---|---:|
| SEV-1 | Learner data exposure, auth bypass, production outage | Same day |
| SEV-2 | Broken consent/export/erasure flow, payment defect | 1 business day |
| SEV-3 | Content correction, lesson quality issue, onboarding bug | 3 business days |
| SEV-4 | General feedback or roadmap request | Best effort |

## Learner-data escalation

Never request unnecessary personal details from a learner. For learner-data issues, involve a guardian/admin contact and use pseudonymous IDs in internal debugging where possible.

## Content correction workflow

Reported content issues are triaged by severity, mapped to CAPS reference, assigned review status, corrected, and included in the correction history before republishing.
