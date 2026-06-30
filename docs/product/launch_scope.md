---
title: "EduBoost beta launch scope"
status: active
owner: product
reviewers: [product, curriculum, release-management]
audience: stakeholder
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/product/README.md]
---

# EduBoost beta launch scope

EduBoost must launch with deliberately bounded claims.

## Supported launch slice with live content evidence

- Grade and subject: Grade 4 Mathematics launch slice.
- CAPS refs: 4.M.1.1, 4.M.1.2, 4.M.1.3.
- Diagnostic content: 40 approved items per launch ref, 120 total.
- Lesson content: 8 approved lessons per launch ref, 24 total.
- Language: English first.
- Evidence: docs/release/runtime_launch_content_evidence_status.md.

## Supported in private beta with boundary controls

- Grades: Grade R to Grade 7 only for topics present in the versioned CAPS topic map and backed by approved content.
- Subjects: Mathematics MVP first; other subjects remain roadmap unless explicit reviewed content exists.
- Lesson types: structured AI-assisted lessons that pass schema, CAPS, PII-redaction, answer-key, and quality-score checks.
- Diagnostics: approved diagnostic items with validated CAPS references and review status.
- Languages: English interface and learner-facing explanations, with multilingual support treated as roadmap.
- Payment modes: free tier only until Stripe checkout, refund handling, and support workflows are verified in staging.

## Unsupported claims

EduBoost must not claim complete CAPS coverage, guaranteed outcomes, teacher replacement, or unrestricted AI tutoring. Public copy should say CAPS-linked beta content unless a topic has validated lessons, diagnostic items, answer keys, and review evidence.

## Launch gates still outside content

A release may progress from private alpha to public beta only after release checklist, CI, branch protection, staging smoke, backup and restore, support workflow, incident response, POPIA workflows, monitoring, and go-no-go evidence are complete.
