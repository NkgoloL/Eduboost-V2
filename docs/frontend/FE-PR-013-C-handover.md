---
title: "FE-PR-013-C Handover \u2014 Parent-review API integration"
status: "current-evidence"
owner: "frontend"
reviewers: "[frontend, product, privacy]"
audience: "developer"
source_of_truth: "false"
supersedes: "[]"
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: "60"
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/frontend, docs/frontend/README.md]"
---

# FE-PR-013-C Handover — Parent-review API integration

This PR integrates the parent-review storage boundary with controlled API surfaces.

Included:

- `app/frontend/src/app/api/tutor/review/route.ts` — POST saves redacted review; GET lists guardian-readable reviews (requires `GUARDIAN_API_KEY` Authorization header)
- `app/frontend/src/lib/tutor/parent-review/access.ts` — simple guardian auth guard (env `GUARDIAN_API_KEY`)
- `app/frontend/src/lib/tutor/parent-review/service.ts` — server-only service wiring redaction + repository + retention filter
- Tests cover API route, access guard, and service integration

Non-goals: voice, microphone, WhatsApp, tutor UI, raw transcript storage, analytics.

Verification instructions are in the project root; run the same checks as prior PRs.
