---
title: "Frontend ADR Sign-Off Register"
status: active
owner: frontend
reviewers: [frontend, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# Frontend ADR Sign-Off Register

| ADR | Title | Status | Required Reviewers | Approval Date | Notes |
| --- | --- | --- | --- | --- | --- |
| ADR-001 | Auth Model | Accepted | Frontend Tech Lead, Backend Lead, POPIA Compliance Officer | 2026-05-28 | Supabase rollback plan recorded. |
| ADR-001 Rollback | Supabase Auth Restoration | Accepted | Frontend Tech Lead, Backend Lead | 2026-05-28 | Executed only if FastAPI auth migration fails. |
| ADR-002 | State Management | Accepted | Frontend Tech Lead, Product Eng Manager | 2026-05-28 | Zustand + TanStack Query baseline. |
| ADR-003 | POPIA Frontend Audit Relay | Accepted | Frontend Tech Lead, POPIA Compliance Officer, Information Officer | 2026-05-28 | Audit relays mandatory for RC2+ actions. |
| ADR-004 | AI Tutor Proxy & Safety | Draft | POPIA Compliance Officer, Information Officer, Safety Lead | — | Pending FE-SPIKE-005 + RC5 gate. |
| ADR-005 | Analytics & Consent Tiers | Draft | POPIA Compliance Officer, Information Officer | — | Moves to Accepted during RC4 once Plausible evidence captured. |
| ADR-006 | RSC Boundaries | Accepted | Frontend Architecture Review Board | 2026-05-28 | PPR explicitly deferred post FE-SPIKE-003. |
| ADR-007 | Offline Sync | Draft | POPIA Compliance Officer, Information Officer | — | Requires FE-SPIKE-006 + RC4 compliance memo. |
| ADR-008 | Voice Input | Draft | POPIA Compliance Officer, Information Officer, Safety Lead | — | Requires FE-SPIKE-004 results. |
