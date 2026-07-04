---
title: "RR-015 External Approvals"
status: active
owner: governance
reviewers: [security, privacy, legal, curriculum, release-management]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-04
review_interval_days: 60
evidence_command: "PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr015_external_approvals.py --json"
code_anchors: [docs/approvals, scripts/approvals]
---

# RR-015 External Approvals

## Register citation

- RR item: `RR-015`
- Register title: `External approval`
- Source: `EduBoost_V2_North_Star_TODO.md`
- Priority: `P0`

## Purpose

RR-015 records the explicit approval artefacts required before any later public-beta activation or release-safety decision can rely on external review.

This slice records external approval evidence only. It does not itself authorise public beta activation, public beta live traffic, expanded learner data migration, production release, deployment, release tagging, billing launch, live payment processing, or runtime KG implementation.

## Required approval classes

- Security review
- POPIA/privacy review
- Legal review
- CAPS/content review
- Release-owner go/no-go signoff

Each approval must include a named approver, date/decision metadata, and an evidence URL or evidence pointer. Repository-only generated templates cannot substitute for external review.

## Explicit boundary

- Public beta expansion authorised: false
- Public beta live traffic authorised: false
- Expanded learner data migration authorised: false
- Billing launch authorised: false
- Live payment processing authorised: false
- Production release authorised: false
- Deployment authorised: false
- Release tag authorised: false
- Runtime KG implementation claimed: false

## Required final evidence outputs

- `docs/approvals/rr015_security_review_attestation.md`
- `docs/approvals/rr015_popia_privacy_review_attestation.md`
- `docs/approvals/rr015_legal_review_attestation.md`
- `docs/approvals/rr015_caps_content_review_attestation.md`
- `docs/approvals/rr015_release_owner_go_no_go_signoff.md`
- `docs/approvals/rr015_external_approval_boundary.md`

## Verification

```bash
PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr015_external_approvals.py --json
```
