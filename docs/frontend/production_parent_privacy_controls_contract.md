---
title: "Production Parent Privacy Controls Contract"
status: active
owner: frontend
reviewers: [frontend, product, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [app/frontend, docs/frontend/README.md]
---

# Production Parent Privacy Controls Contract

## Purpose

This contract defines parent/guardian privacy and data-rights UX requirements.

## Required Controls

- Show consent status.
- Show privacy controls.
- Add data export request UI.
- Add erasure request UI.
- Add data correction request UI.
- Add processing restriction request UI.
- Add consent renewal UI.
- Preserve canonical POPIA envelope error handling.
- Preserve parent/guardian authorization boundary.

## Repository Evidence

- `app/frontend/src/app/(parent)/parent-dashboard/page.tsx`
- `app/frontend/src/app/parent-portal/page.tsx`
- `app/frontend/src/lib/api/services.ts`
- `docs/frontend/parent_vertical_journey_contract.md`
- `docs/frontend/frontend_auth_consent_denial_contract.md`
