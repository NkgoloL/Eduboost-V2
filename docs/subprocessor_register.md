---
title: "Subprocessor Register (Repository)"
status: "active"
owner: "compliance"
reviewers: ['compliance', 'legal', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Subprocessor Register (Repository)

| Subprocessor | Purpose | Data exposure | Status |
|---|---|---|---|
| PostgreSQL hosting provider | Primary application database | Guardian/learner operational data | Required production processor |
| Redis hosting provider | Cache, rate limits, token/session revocation | Session metadata, no learner content | Required production processor |
| SendGrid or configured email provider | Transactional email | Guardian email address, template metadata | Pending production selection |
| Stripe | Billing/subscriptions | Guardian billing/customer metadata | Pending production selection |
| PostHog | Product analytics | Pseudonymous events only | Optional; no raw learner PII |
| Anthropic/Groq/local HF provider | LLM lesson generation | Pseudonymous educational context only | Provider depends on deployment config |
| Azure Blob/Object storage | Backups/assets/exports if enabled | Encrypted objects | Pending production selection |

Before production launch, each active subprocessor must have: contract/DPA status, region, retention behavior, breach-notification terms, and offboarding procedure recorded.
