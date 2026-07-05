---
title: "FE-PR-013-D Voice Consent Evidence"
status: "current-evidence"
owner: "frontend"
reviewers: ["frontend", "product", "privacy"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/frontend, docs/frontend/README.md]"
---

# FE-PR-013-D Voice Consent Evidence

- Guardian consent stored in `localStorage` via `app/frontend/src/lib/voice/consent.ts`.
- Consent is required for voice usage; guardrails implemented in `guardrails.ts`.
- No microphone permission is requested on component mount; permission flows must be user-initiated in the UI.
- Tests cover consent get/set, guardrails logic, capability detection, and component render.
